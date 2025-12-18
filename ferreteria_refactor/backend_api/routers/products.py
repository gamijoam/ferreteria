from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from ..database.db import get_db
from ..models import models
from .. import schemas
from ..dependencies import has_role
from ..models.models import UserRole
from ..websocket.manager import manager
from ..websocket.events import WebSocketEvents

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_model=List[schemas.ProductRead])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = db.query(models.Product).options(joinedload(models.Product.units)).filter(models.Product.is_active == True).offset(skip).limit(limit).all()
    return products

@router.post("/", response_model=schemas.ProductRead, dependencies=[Depends(has_role([UserRole.ADMIN, UserRole.WAREHOUSE]))])
async def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    # Exclude 'units' from the main Product creation
    product_data = product.dict(exclude={"units"})
    db_product = models.Product(**product_data)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    # Process Units
    if product.units:
        for unit in product.units:
            db_unit = models.ProductUnit(**unit.dict(), product_id=db_product.id)
            db.add(db_unit)
        db.commit()
        db.refresh(db_product)
        
    # Simplify broadcast data to avoid serialization issues with complex objects
    # Or just send ID and let frontend fetch? Better to send key data.
    await manager.broadcast(WebSocketEvents.PRODUCT_CREATED, {
        "id": db_product.id,
        "name": db_product.name,
        "price": db_product.price,
        "stock": db_product.stock,
        "exchange_rate_id": db_product.exchange_rate_id
    })
        
    return db_product

@router.put("/{product_id}", response_model=schemas.ProductRead, dependencies=[Depends(has_role([UserRole.ADMIN, UserRole.WAREHOUSE]))])
async def update_product(product_id: int, product_update: schemas.ProductUpdate, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = product_update.dict(exclude_unset=True)
    
    # Separate units data if present
    units_data = None
    if "units" in update_data:
        units_data = update_data.pop("units")

    # Prepare BEFORE state for audit
    # We create a simple dict representation or clone object attributes
    # Ideally, we use the helper from audit_utils which handles models
    # But here db_product is attached to session.
    # To avoid issues with session refresh, we might want to capture dict now.
    from ..audit_utils import log_action
    
    # Simple snapshot of relevant fields before update
    # or rely on calculate_diff handling the model directly if we pass a copy?
    # Easier: Convert to dict manually for the "old" state before applying changes
    old_state = {c.name: getattr(db_product, c.name) for c in db_product.__table__.columns}

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

    db.commit()
    db.refresh(db_product)
    
    # LOG ACTION
    # We pass the old_state dict as "before" and the refreshed db_product as "after"
    user_id = 1 # TODO: Get from current user dependency if available, otherwise 1 (System/Admin)
    # The routers/products.py dependencies don't inject 'current_user' into the function, only check roles.
    # We should update function sig to get user ID if we want strict attribution.
    # For now, we'll try to get it if added to params, or default to None.
    
    # Let's improve this: Add user dependency or placeholder
    
    # Calculate diff manually since we have dict vs model
    # audit_utils.calculate_diff handles model vs model usually. 
    # Let's construct a temp object or just use a specialized diff logic?
    # Actually, let's just use log_action with the manual diff.
    
    new_state = {c.name: getattr(db_product, c.name) for c in db_product.__table__.columns}
    
    # Calculate diff
    import json
    changes = {}
    for k, v in new_state.items():
        if k in old_state and old_state[k] != v:
            changes[k] = {"old": old_state[k], "new": v}
            
    if changes:
        log_action(db, user_id=1, action="UPDATE", table_name="products", record_id=db_product.id, changes=json.dumps(changes, default=str))


    await manager.broadcast(WebSocketEvents.PRODUCT_UPDATED, {
        "id": db_product.id,
        "name": db_product.name,
        "price": db_product.price,
        "stock": db_product.stock,
        "exchange_rate_id": db_product.exchange_rate_id
    })
    
    return db_product



@router.get("/{product_id}", response_model=schemas.ProductRead)
def read_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).options(joinedload(models.Product.units)).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.delete("/{product_id}", dependencies=[Depends(has_role([UserRole.ADMIN]))])
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Soft delete (set inactive)
    product.is_active = False
    db.commit()
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
async def create_sale(sale_data: schemas.SaleCreate, db: Session = Depends(get_db)):
    from ..services.sales_service import SalesService
    
    # Delegate to Service
    # TODO: Get actual user_id from dependency
    return await SalesService.create_sale(db, sale_data, user_id=1)

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
                # Check for existing SKU to avoid generic IntegrityError if possible (optimization)
                # But begin_nested handles it safely.
                # db_product = models.Product(**p.dict()) 
                # p.dict() might invoke validations.
                
                # Manual mapping or dict unpacking
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
