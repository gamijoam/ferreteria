from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from fastapi import HTTPException, BackgroundTasks
from decimal import Decimal
import requests
from ..models import models
from .. import schemas
from ..websocket.manager import manager
from ..websocket.events import WebSocketEvents
import asyncio

# DUPLICATED HELPER due to circular import risks if we try to import from routers
def run_broadcast(event: str, data: dict):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(manager.broadcast(event, data))
    finally:
        loop.close()

class SalesService:
    @staticmethod
    def create_sale(db: Session, sale_data: schemas.SaleCreate, user_id: int, background_tasks: BackgroundTasks = None):
        updated_products_info = []
        
        # Credit Validation for Credit Sales
        if sale_data.is_credit and sale_data.customer_id:
            customer = db.query(models.Customer).filter(models.Customer.id == sale_data.customer_id).first()
            if not customer:
                raise HTTPException(status_code=404, detail="Customer not found")
            
            # 1. Check if customer is blocked
            if customer.is_blocked:
                raise HTTPException(
                    status_code=400,
                    detail=f"Cliente '{customer.name}' está bloqueado por mora. No se pueden realizar ventas a crédito."
                )
            
            # 2. Check for overdue invoices
            overdue_count = db.query(models.Sale).filter(
                models.Sale.customer_id == sale_data.customer_id,
                models.Sale.is_credit == True,
                models.Sale.paid == False,
                models.Sale.due_date < datetime.now()
            ).count()
            
            if overdue_count > 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"Cliente tiene {overdue_count} factura(s) vencida(s). Debe ponerse al día antes de nuevas ventas a crédito."
                )
            
            # 3. Check credit limit
            current_debt = db.query(func.sum(models.Sale.balance_pending)).filter(
                models.Sale.customer_id == sale_data.customer_id,
                models.Sale.is_credit == True,
                models.Sale.paid == False
            ).scalar() or Decimal("0.00")
            
            if (current_debt + sale_data.total_amount) > customer.credit_limit:
                raise HTTPException(
                    status_code=400,
                    detail=f"Excede límite de crédito. Deuda actual: ${current_debt:.2f}, Límite: ${customer.credit_limit:.2f}, Disponible: ${(customer.credit_limit - current_debt):.2f}"
                )
        
        # 1. Create Sale Header
        total_bs = sale_data.total_amount * sale_data.exchange_rate
        
        # Calculate due date for credit sales
        due_date = None
        balance_pending = None
        if sale_data.is_credit and sale_data.customer_id:
            customer = db.query(models.Customer).filter(models.Customer.id == sale_data.customer_id).first()
            if customer:
                due_date = datetime.now() + timedelta(days=customer.payment_term_days)
                balance_pending = sale_data.total_amount
        
        new_sale = models.Sale(
            total_amount=sale_data.total_amount,
            payment_method=sale_data.payment_method,
            customer_id=sale_data.customer_id,
            is_credit=sale_data.is_credit,
            paid=not sale_data.is_credit, 
            currency=sale_data.currency,
            exchange_rate_used=sale_data.exchange_rate,
            total_amount_bs=total_bs,
            notes=sale_data.notes,
            due_date=due_date,
            balance_pending=balance_pending,
            # user_id=user_id # TODO: Uncomment when user_id is added to Sale model
        )
        db.add(new_sale)
        db.flush() # Get ID
    
        # 2. Process Items
        for item in sale_data.items:
            # Fetch Product with Pessimistic Lock
            product = db.query(models.Product).filter(models.Product.id == item.product_id).with_for_update().first()
            if not product:
                raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
            
            # Calculate base units to deduct using conversion_factor
            units_to_deduct = item.quantity * item.conversion_factor
            
            # NEW: COMBO LOGIC - Check if product is a combo
            if product.is_combo:
                # COMBO: Don't check/deduct stock from parent, process children instead
                if not product.combo_items:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Combo product '{product.name}' has no components defined"
                    )
                
                # Check stock for ALL child products first (fail fast)
                for combo_item in product.combo_items:
                    child_product = combo_item.child_product
                    
                    # NEW: Calculate quantity considering unit presentation
                    if combo_item.unit_id and combo_item.unit:
                        # If specific unit is defined, use its conversion factor
                        conversion_factor = combo_item.unit.conversion_factor
                        qty_needed = item.quantity * combo_item.quantity * conversion_factor
                    else:
                        # No unit specified, use base quantity
                        qty_needed = item.quantity * combo_item.quantity
                    
                    if child_product.stock < qty_needed:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Insufficient stock for combo component '{child_product.name}'. Needed: {qty_needed}, Available: {child_product.stock}"
                        )
                
                # All checks passed, now deduct stock from children
                for combo_item in product.combo_items:
                    child_product = combo_item.child_product
                    
                    # NEW: Calculate quantity considering unit presentation
                    if combo_item.unit_id and combo_item.unit:
                        # If specific unit is defined, use its conversion factor
                        conversion_factor = combo_item.unit.conversion_factor
                        qty_to_deduct = item.quantity * combo_item.quantity * conversion_factor
                        unit_description = f" ({combo_item.quantity}x {combo_item.unit.unit_name})"
                    else:
                        # No unit specified, use base quantity
                        qty_to_deduct = item.quantity * combo_item.quantity
                        unit_description = ""
                    
                    # Deduct stock from child
                    child_product.stock -= qty_to_deduct
                    
                    # Create Kardex entry for child product
                    kardex_entry = models.Kardex(
                        product_id=child_product.id,
                        movement_type="SALE",
                        quantity=-qty_to_deduct,
                        balance_after=child_product.stock,
                        description=f"Sale via combo: {product.name}{unit_description} (Sale #{new_sale.id})"
                    )
                    db.add(kardex_entry)
                    
                    # Collect child product info for broadcast
                    updated_products_info.append({
                        "id": child_product.id,
                        "name": child_product.name,
                        "price": float(child_product.price),
                        "stock": float(child_product.stock),
                        "exchange_rate_id": child_product.exchange_rate_id
                    })
            else:
                # NORMAL PRODUCT: Check and deduct stock as usual
                if product.stock < units_to_deduct:
                    raise HTTPException(status_code=400, detail=f"Insufficient stock for {product.name}")
                
                # Update Stock
                product.stock -= units_to_deduct
                
                # Collect info for broadcast
                updated_products_info.append({
                    "id": product.id,
                    "name": product.name,
                    "price": float(product.price),
                    "stock": float(product.stock),
                    "exchange_rate_id": product.exchange_rate_id
                })
                
                # Register Kardex Movement
                kardex_entry = models.Kardex(
                    product_id=product.id,
                    movement_type="SALE",
                    quantity=-units_to_deduct,
                    balance_after=product.stock,
                    description=f"Sale #{new_sale.id}: Sold {item.quantity} units at ${item.unit_price_usd} each"
                )
                db.add(kardex_entry)
            
            # Calculate subtotal (before discount) - SAME FOR BOTH
            subtotal = item.unit_price_usd * item.quantity
            
            # Apply discount if any
            if item.discount > 0:
                if item.discount_type == "PERCENT":
                    subtotal = subtotal * (1 - item.discount / 100)
                elif item.discount_type == "FIXED":
                    subtotal = subtotal - item.discount
            
            # Create Sale Detail - SAME FOR BOTH
            detail = models.SaleDetail(
                sale_id=new_sale.id,
                product_id=product.id,
                quantity=units_to_deduct,
                unit_price=item.unit_price_usd,
                subtotal=subtotal,
                is_box_sale=False,
                discount=item.discount,
                discount_type=item.discount_type
            )
            db.add(detail)
    
        # 3. Process Payments (New Multi-Payment Logic)
        if sale_data.payments:
            for p in sale_data.payments:
                new_payment = models.SalePayment(
                    sale_id=new_sale.id,
                    amount=p.amount,
                    currency=p.currency,
                    payment_method=p.payment_method,
                    exchange_rate=p.exchange_rate
                )
                db.add(new_payment)
        else:
            # Fallback for legacy calls or single payment
            fallback_payment = models.SalePayment(
                sale_id=new_sale.id,
                amount=sale_data.total_amount,
                currency=sale_data.currency,
                payment_method=sale_data.payment_method,
                exchange_rate=sale_data.exchange_rate
            )
            db.add(fallback_payment)
        
        db.commit()
        
        # Emit Stock Update Events using BackgroundTasks
        if background_tasks:
            for p_info in updated_products_info:
                background_tasks.add_task(run_broadcast, WebSocketEvents.PRODUCT_UPDATED, p_info)
                background_tasks.add_task(run_broadcast, WebSocketEvents.PRODUCT_STOCK_UPDATED, {
                    "id": p_info["id"], 
                    "stock": p_info["stock"]
                })
            
            # Emit Sale Event
            background_tasks.add_task(run_broadcast, WebSocketEvents.SALE_COMPLETED, {
                "id": new_sale.id,
                "total_amount": float(new_sale.total_amount),
                "currency": new_sale.currency,
                "payment_method": new_sale.payment_method,
                "customer_id": new_sale.customer_id,
                "date": new_sale.date.isoformat() if new_sale.date else None
            })
            
            # AUTO-PRINT TICKET
            background_tasks.add_task(print_sale_ticket, new_sale.id)
            
        return {"status": "success", "sale_id": new_sale.id}

def print_sale_ticket(sale_id: int):
    """
    Print ticket for a completed sale
    Sends sale data to hardware bridge for printing
    """
    from ..database.db import SessionLocal
    import json # For debug dumping
    
    print(f"🖨️ START PRINT JOB: Sale #{sale_id}")
    
    # Create new database session for background task
    db = SessionLocal()
    
    try:
        # Get sale with all relationships
        sale = db.query(models.Sale).filter(models.Sale.id == sale_id).first()
        if not sale:
            print(f"❌ Sale {sale_id} not found for printing")
            return
        
        # Get business info
        business_config = {}
        configs = db.query(models.BusinessConfig).all()
        for config in configs:
            # print(f"DEBUG DB: {config.key} = {config.value}") 
            business_config[config.key] = config.value
            
        print(f"   Loaded {len(business_config)} config keys. Business Name: '{business_config.get('business_name')}'")
        
        # Get ticket template
        template = business_config.get('ticket_template')
        if not template:
            print("⚠️  No ticket template configured, skipping print")
            return
            
        print(f"   Template found (len={len(template)})")
        
        # Build context for template
        context = {
            "business": {
                "name": business_config.get('business_name', 'MI NEGOCIO'),
                "document_id": business_config.get('business_doc', ''),
                "address": business_config.get('business_address', ''),
                "phone": business_config.get('business_phone', ''),
                "email": business_config.get('business_email', '')
            },
            "sale": {
                "id": sale.id,
                "date": sale.date.strftime("%d/%m/%Y %H:%M") if sale.date else "",
                "total": float(sale.total_amount),
                "is_credit": sale.is_credit,
                "balance": float(sale.balance_pending) if sale.balance_pending else 0.0,
                "customer": {
                    "name": sale.customer.name if sale.customer else None,
                    "id_number": sale.customer.id_number if sale.customer else None
                } if sale.customer else None,
                "items": [
                    {
                        "product": {"name": item.product.name if item.product else "Producto"},
                        "quantity": float(item.quantity),
                        "unit_price": float(item.unit_price),
                        "subtotal": float(item.subtotal)
                    }
                    for item in sale.details
                ]
            }
        }
        # Add alias 'products' to avoid Jinja collision with dict.items()
        context["sale"]["products"] = context["sale"]["items"]
        
        print("   Context built successfully")
        
        # Send to hardware bridge
        print(f"   Sending to http://localhost:5001/print...")
        
        # DEBUG: Print payload preview
        # print(json.dumps(context, indent=2, default=str)) 
        
        response = requests.post(
            "http://localhost:5001/print",
            json={
                "template": template,
                "context": context
            },
            timeout=5
        )
        
        print(f"   Bridge Response: {response.status_code} - {response.text}")
        
        if response.status_code == 200:
            print(f"✅ Ticket printed for sale #{sale_id}")
        else:
            print(f"⚠️  Print failed for sale #{sale_id}: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ BRIDGE ERROR: Hardware bridge not available (port 5001)")
    except Exception as e:
        print(f"❌ PRINT EXCEPTION: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
