from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from fastapi import HTTPException
from decimal import Decimal  # NEW
from ..models import models
from .. import schemas
from ..websocket.manager import manager
from ..websocket.events import WebSocketEvents

class SalesService:
    @staticmethod
    async def create_sale(db: Session, sale_data: schemas.SaleCreate, user_id: int):
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
            # SQLAlchemy returns Decimal for Numeric columns, but scalar() might return None
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
            # item.conversion_factor and item.quantity are Decimals from schema
            units_to_deduct = item.quantity * item.conversion_factor
            
            # Check Stock
            if product.stock < units_to_deduct:
                 raise HTTPException(status_code=400, detail=f"Insufficient stock for {product.name}")
    
            # Calculate subtotal (before discount)
            subtotal = item.unit_price_usd * item.quantity
            
            # Apply discount if any
            if item.discount > 0:
                if item.discount_type == "PERCENT":
                    subtotal = subtotal * (1 - item.discount / 100)
                elif item.discount_type == "FIXED":
                    subtotal = subtotal - item.discount
            
            # Create Sale Detail
            detail = models.SaleDetail(
                sale_id=new_sale.id,
                product_id=product.id,
                quantity=units_to_deduct,  # Store base units deducted
                unit_price=item.unit_price_usd,  # Store the price per unit sold
                subtotal=subtotal,
                is_box_sale=False,  # Deprecated, keeping for compatibility
                discount=item.discount,
                discount_type=item.discount_type
            )
            db.add(detail)
    
            # Update Stock
            product.stock -= units_to_deduct
            
            # Collect info for broadcast
            updated_products_info.append({
                "id": product.id,
                "name": product.name,
                "price": float(product.price), # Cast to float for JSON
                "stock": float(product.stock),
                "exchange_rate_id": product.exchange_rate_id
            })
            
            # Register Kardex Movement
            kardex_entry = models.Kardex(
                product_id=product.id,
                movement_type="SALE",
                quantity=-units_to_deduct,  # Negative for outgoing
                balance_after=product.stock,
                description=f"Sale #{new_sale.id}: Sold {item.quantity} units at ${item.unit_price_usd} each"
            )
            db.add(kardex_entry)
    
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
        
        # Emit Stock Update Events
        for p_info in updated_products_info:
            await manager.broadcast(WebSocketEvents.PRODUCT_UPDATED, p_info)
            await manager.broadcast(WebSocketEvents.PRODUCT_STOCK_UPDATED, {
                "id": p_info["id"], 
                "stock": p_info["stock"]
            })
        
        # Emit Sale Event
        await manager.broadcast(WebSocketEvents.SALE_COMPLETED, {
            "id": new_sale.id,
            "total_amount": float(new_sale.total_amount), # Cast for JSON
            "currency": new_sale.currency,
            "payment_method": new_sale.payment_method,
            "customer_id": new_sale.customer_id,
            "date": new_sale.date.isoformat() if new_sale.date else None
        })
            
        return {"status": "success", "sale_id": new_sale.id}
