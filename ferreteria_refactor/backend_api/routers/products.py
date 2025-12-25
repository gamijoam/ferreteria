from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session, joinedload
from typing import List
import json
import asyncio
from ..database.db import get_db
from ..models import models
from ..models.models import UserRole
from .. import schemas
from ..dependencies import has_role
from ..websocket.manager import manager
from ..websocket.events import WebSocketEvents
from ..audit_utils import log_action

router = APIRouter(prefix="/products", tags=["products"])

# Helper para ejecutar broadcast asíncrono desde contexto síncrono
def run_broadcast(event: str, data: dict):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(manager.broadcast(event, data))
    finally:
        loop.close()

@router.get("/", response_model=List[schemas.ProductRead])
@router.get("", response_model=List[schemas.ProductRead], include_in_schema=False)
def read_products(skip: int = 0, limit: int = 5000, db: Session = Depends(get_db)):
    try:
        products = db.query(models.Product).options(joinedload(models.Product.units)).filter(models.Product.is_active == True).offset(skip).limit(limit).all()
        print(f"✅ Loaded {len(products)} products successfully")
        return products
    except Exception as e:
        print(f"❌ ERROR loading products: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error loading products: {str(e)}")

@router.post("/", response_model=schemas.ProductRead, dependencies=[Depends(has_role([UserRole.ADMIN, UserRole.WAREHOUSE]))])
@router.post("", response_model=schemas.ProductRead, dependencies=[Depends(has_role([UserRole.ADMIN, UserRole.WAREHOUSE]))], include_in_schema=False)
def create_product(product: schemas.ProductCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # 1. Operaciones DB (Síncronas en Threadpool)
    product_data = product.dict(exclude={"units", "combo_items"})
    db_product = models.Product(**product_data)
    db.add(db_product)
    try:
        db.commit()
        db.refresh(db_product)
    except Exception as e:
        db.rollback()
        if "unique" in str(e).lower() or "duplicate" in str(e).lower():
            raise HTTPException(status_code=400, detail="Product with this SKU or Name already exists")
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")

    # Process Units
    if product.units:
        for unit in product.units:
            db_unit = models.ProductUnit(**unit.dict(), product_id=db_product.id)
            db.add(db_unit)
    
    try:
        db.commit()
        db.refresh(db_product)
    except Exception as e:
        db.rollback()
        error_msg = str(e).lower()
        if "unique" in error_msg or "duplicate" in error_msg:
             raise HTTPException(status_code=400, detail=f"Error: SKU or Name already exists. ({str(e)})")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    # NEW: Process Combo Items
    if product.combo_items:
        for combo_item in product.combo_items:
            db_combo_item = models.ComboItem(
                parent_product_id=db_product.id,
                child_product_id=combo_item.child_product_id,
                quantity=combo_item.quantity,
                unit_id=combo_item.unit_id  # NEW: Include unit_id
            )
            db.add(db_combo_item)
        db.commit()
        db.refresh(db_product)
        
    # 2. WebSocket en Background
    payload = {
        "id": db_product.id,
        "name": db_product.name,
        "price": float(db_product.price),
        "stock": float(db_product.stock),
        "is_combo": db_product.is_combo,
        "exchange_rate_id": db_product.exchange_rate_id,
        "units": [
            {
                "id": u.id,
                "unit_name": u.unit_name,
                "conversion_factor": float(u.conversion_factor),
                "price_usd": float(u.price_usd) if u.price_usd else None,
                "barcode": u.barcode
            } for u in db_product.units
        ] if db_product.units else [],
        "combo_items": [
            {
                "id": c.id,
                "child_product_id": c.child_product_id,
                "quantity": float(c.quantity)
            } for c in db_product.combo_items
        ] if db_product.combo_items else []
    }
    background_tasks.add_task(run_broadcast, WebSocketEvents.PRODUCT_CREATED, payload)
        
    return db_product

@router.put("/{product_id}", response_model=schemas.ProductRead, dependencies=[Depends(has_role([UserRole.ADMIN, UserRole.WAREHOUSE]))])
def update_product(product_id: int, product_update: schemas.ProductUpdate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = product_update.dict(exclude_unset=True)
    
    # Separate units data if present
    units_data = None
    if "units" in update_data:
        units_data = update_data.pop("units")
    
    # NEW: Separate combo_items data if present
    combo_items_data = None
    if "combo_items" in update_data:
        combo_items_data = update_data.pop("combo_items")

    # Capture Current State (Old)
    old_state = {c.name: getattr(db_product, c.name) for c in db_product.__table__.columns}

    # Apply Updates
    for key, value in update_data.items():
        setattr(db_product, key, value)
    
    # Handle Units Update (Snapshot Strategy: Delete all old, create new)
    if units_data is not None:
        # Delete existing units
        db.query(models.ProductUnit).filter(models.ProductUnit.product_id == product_id).delete()
        
        # Add new units
        for unit in units_data:
            db_unit = models.ProductUnit(**unit, product_id=product_id)
            db.add(db_unit)
    
    # NEW: Handle Combo Items Update (Snapshot Strategy)
    if combo_items_data is not None:
        # Delete existing combo items
        db.query(models.ComboItem).filter(
            models.ComboItem.parent_product_id == product_id
        ).delete()
        
        # Add new combo items
        for combo_item in combo_items_data:
            db_combo_item = models.ComboItem(
                parent_product_id=product_id,
                child_product_id=combo_item["child_product_id"],
                quantity=combo_item["quantity"],
                unit_id=combo_item.get("unit_id")  # NEW: Include unit_id
            )
            db.add(db_combo_item)

    db.commit()
    db.refresh(db_product)
    
    # Logic Refactor: Audit (Simplified)
    user_id = 1 # TODO: Get from current_user
    new_state = {c.name: getattr(db_product, c.name) for c in db_product.__table__.columns}
    
    changes = {}
    for k, v in new_state.items():
        if k in old_state and old_state[k] != v:
            changes[k] = {"old": old_state[k], "new": v}
            
    if changes:
        log_action(db, user_id=user_id, action="UPDATE", table_name="products", record_id=db_product.id, changes=json.dumps(changes, default=str))

    # Broadcast
    payload = {
        "id": db_product.id,
        "name": db_product.name,
        "price": float(db_product.price),
        "stock": float(db_product.stock),
        "is_combo": db_product.is_combo,
        "exchange_rate_id": db_product.exchange_rate_id,
        "units": [
            {
                "id": u.id,
                "unit_name": u.unit_name,
                "conversion_factor": float(u.conversion_factor),
                "price_usd": float(u.price_usd) if u.price_usd else None,
                "barcode": u.barcode
            } for u in db_product.units
        ] if db_product.units else [],
        "combo_items": [
            {
                "id": c.id,
                "child_product_id": c.child_product_id,
                "quantity": float(c.quantity)
            } for c in db_product.combo_items
        ] if db_product.combo_items else []
    }
    background_tasks.add_task(run_broadcast, WebSocketEvents.PRODUCT_UPDATED, payload)
    
    return db_product

@router.get("/{product_id}", response_model=schemas.ProductRead)
def read_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).options(joinedload(models.Product.units)).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.delete("/{product_id}", dependencies=[Depends(has_role([UserRole.ADMIN]))])
def delete_product(product_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Soft delete (set inactive)
    product.is_active = False
    db.commit()
    
    # Broadcast product deleted/deactivated
    payload = {
        "id": product.id,
        "name": product.name
    }
    background_tasks.add_task(run_broadcast, WebSocketEvents.PRODUCT_DELETED, payload)
    
    return {"status": "success", "message": "Product deactivated"}

# ========================================
# PRICE CALCULATION UTILITY
# ========================================

@router.post("/calculate-price")
def calculate_price(
    price_usd: float,
    exchange_rate_id: int = None,
    db: Session = Depends(get_db)
):
    """
    Calculate prices in all currencies using a specific exchange rate.
    If exchange_rate_id is provided, use that rate.
    Otherwise, use default rates for each currency.
    """
    if exchange_rate_id:
        # Use specific rate
        rate = db.query(models.ExchangeRate).get(exchange_rate_id)
        if not rate or not rate.is_active:
            raise HTTPException(status_code=404, detail="Exchange rate not found or inactive")
        
        return {
            "price_usd": price_usd,
            "exchange_rate": {
                "id": rate.id,
                "name": rate.name,
                "currency_code": rate.currency_code,
                "rate": rate.rate
            },
            "converted_price": price_usd * rate.rate,
            "currency_symbol": rate.currency_symbol
        }
    else:
        # Calculate for all active default rates
        default_rates = db.query(models.ExchangeRate).filter(
            models.ExchangeRate.is_default == True,
            models.ExchangeRate.is_active == True
        ).all()
        
        results = []
        for rate in default_rates:
            results.append({
                "currency_code": rate.currency_code,
                "currency_symbol": rate.currency_symbol,
                "rate_name": rate.name,
                "exchange_rate": rate.rate,
                "converted_price": price_usd * rate.rate
            })
        
        return {
            "price_usd": price_usd,
            "conversions": results
        }

@router.get("/{product_id}/rules", response_model=List[schemas.PriceRuleRead])
def read_price_rules(product_id: int, db: Session = Depends(get_db)):
    rules = db.query(models.PriceRule).filter(models.PriceRule.product_id == product_id).order_by(models.PriceRule.min_quantity).all()
    return rules

@router.post("/{product_id}/rules", response_model=schemas.PriceRuleRead)
def create_price_rule(product_id: int, rule: schemas.PriceRuleCreate, db: Session = Depends(get_db)):
    db_rule = models.PriceRule(**rule.dict())
    db_rule.product_id = product_id # Override with path param
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule

@router.delete("/rules/{rule_id}")
def delete_price_rule(rule_id: int, db: Session = Depends(get_db)):
    rule = db.query(models.PriceRule).filter(models.PriceRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    db.delete(rule)
    db.commit()
    return {"status": "success"}

@router.post("/sales/")
def create_sale(sale_data: schemas.SaleCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    from ..services.sales_service import SalesService
    
    # Delegate to Service (Now Sync)
    # TODO: Get actual user_id from dependency
    return SalesService.create_sale(db, sale_data, user_id=1, background_tasks=background_tasks)

# NEW: Get sale detail with items (for invoice detail view)
@router.get("/sales/{sale_id}", response_model=schemas.SaleRead)
def get_sale_detail(sale_id: int, db: Session = Depends(get_db)):
    """Get sale with details (items/products) for invoice view"""
    sale = db.query(models.Sale).options(
        joinedload(models.Sale.details).joinedload(models.SaleDetail.product),
        joinedload(models.Sale.customer),
        joinedload(models.Sale.payments)
    ).filter(models.Sale.id == sale_id).first()
    
    
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    
    return sale

@router.post("/sales/{sale_id}/print")
def print_sale_endpoint(sale_id: int, db: Session = Depends(get_db)):
    """
    Get print payload for client-side printing.
    Returns template and context for the Hardware Bridge.
    """
    from ..services.sales_service import SalesService
    
    # Now returns JSON { template, context, status }
    return SalesService.get_sale_print_payload(db, sale_id)

@router.post("/sales/payments")
def register_sale_payment(
    payment_data: schemas.SalePaymentCreate,
    db: Session = Depends(get_db)
):
    """Register a payment (abono) for a credit sale"""
    # Verify sale exists
    sale = db.query(models.Sale).filter(models.Sale.id == payment_data.sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    
    # Create SalePayment record
    payment = models.SalePayment(
        sale_id=payment_data.sale_id,
        amount=payment_data.amount,
        currency=payment_data.currency,
        payment_method=payment_data.payment_method,
        exchange_rate=payment_data.exchange_rate
    )
    db.add(payment)
    db.commit()
    
    return {"status": "success", "payment_id": payment.id}

@router.put("/sales/{sale_id}")
def update_sale(
    sale_id: int,
    balance_pending: float = None,
    paid: bool = None,
    db: Session = Depends(get_db)
):
    """Update sale balance and paid status"""
    print(f"🔄 UPDATE SALE {sale_id}: balance_pending={balance_pending}, paid={paid}")
    
    sale = db.query(models.Sale).filter(models.Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    
    print(f"   Before: paid={sale.paid}, balance={sale.balance_pending}")
    
    if balance_pending is not None:
        sale.balance_pending = balance_pending
    
    if paid is not None:
        sale.paid = paid
    
    db.commit()
    db.refresh(sale)
    
    print(f"   After: paid={sale.paid}, balance={sale.balance_pending}")
    
    return {"status": "success", "sale": sale}

@router.post("/bulk", response_model=schemas.BulkImportResult)
def bulk_create_products(products: List[schemas.ProductCreate], db: Session = Depends(get_db)):
    # Initialize result using Pydantic model
    result = schemas.BulkImportResult(success_count=0, failed_count=0, errors=[])
    
    for p in products:
        try:
            # Use nested transaction (savepoint) to isolate each insertion
            with db.begin_nested():
                db_product = models.Product(
                    name=p.name,
                    sku=p.sku,
                    price=p.price,
                    cost_price=p.cost_price,
                    stock=p.stock,
                    description=p.description,
                    min_stock=p.min_stock,
                    is_box=p.is_box,
                    conversion_factor=p.conversion_factor,
                    category_id=p.category_id,
                    supplier_id=p.supplier_id,
                    is_active=True # Default true for imports
                )
                db.add(db_product)
                db.flush() # Force SQL execution to catch constraints
            
            result.success_count += 1
        except Exception as e:
            result.failed_count += 1
            msg = str(e)
            if "UNIQUE constraint failed" in msg or "Duplicate entry" in msg:
                msg = f"SKU '{p.sku}' ya existe."
            result.errors.append(f"Producto '{p.name}': {msg}")
            
    db.commit()
    return result
