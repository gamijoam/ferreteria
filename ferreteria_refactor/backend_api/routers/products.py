from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database.db import get_db
from ..models import models
from .. import schemas
from ..dependencies import has_role, get_current_active_user
from ..models.models import UserRole

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_model=List[schemas.ProductRead])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = db.query(models.Product).filter(models.Product.is_active == True).offset(skip).limit(limit).all()
    return products

@router.post("/", response_model=schemas.ProductRead, dependencies=[Depends(has_role([UserRole.ADMIN, UserRole.WAREHOUSE]))])
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.put("/{product_id}", response_model=schemas.ProductRead)
def update_product(product_id: int, product_update: schemas.ProductUpdate, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = product_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product

    db.commit()
    db.refresh(db_product)
    return db_product

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
def create_sale(sale_data: schemas.SaleCreate, db: Session = Depends(get_db)):
    # 1. Create Sale Header
    total_bs = sale_data.total_amount * sale_data.exchange_rate
    
    new_sale = models.Sale(
        total_amount=sale_data.total_amount,
        payment_method=sale_data.payment_method,
        customer_id=sale_data.customer_id,
        is_credit=sale_data.is_credit,
        paid=not sale_data.is_credit, 
        currency=sale_data.currency,
        exchange_rate_used=sale_data.exchange_rate,
        total_amount_bs=total_bs,
        notes=sale_data.notes
    )
    db.add(new_sale)
    db.flush() # Get ID

    # 2. Process Items
    for item in sale_data.items:
        # Fetch Product
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        
        # Calculate Units to Deduct
        units_to_deduct = item.quantity
        price_used = product.price
        if item.is_box:
            units_to_deduct = item.quantity * product.conversion_factor
            price_used = product.price * product.conversion_factor # Assuming price is per unit, check logic
        
        # Check Stock
        if product.stock < units_to_deduct:
             raise HTTPException(status_code=400, detail=f"Insufficient stock for {product.name}")

        # Create Detail
        # Recalculate subtotal based on backend pricing to be safe? 
        # For now, trust the implicit math: price * qty
        # Note: Discount logic should modify 'subtotal' if we want to be precise, skipping complex calc for now
        subtotal = price_used * item.quantity 
        
        detail = models.SaleDetail(
            sale_id=new_sale.id,
            product_id=product.id,
            quantity=units_to_deduct, # Deduct base units
            unit_price=product.price, # Store base unit price
            subtotal=subtotal,
            is_box_sale=item.is_box,
            discount=item.discount,
            discount_type=item.discount_type
        )
        db.add(detail)

        # Update Stock
        product.stock -= units_to_deduct

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
        # Create a single payment entry based on the sale header info
        fallback_payment = models.SalePayment(
            sale_id=new_sale.id,
            amount=sale_data.total_amount,
            currency=sale_data.currency,
            payment_method=sale_data.payment_method,
            exchange_rate=sale_data.exchange_rate
        )
        db.add(fallback_payment)

    db.commit()
    return {"status": "success", "sale_id": new_sale.id}

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

# ===== PRODUCT UNITS / PRESENTATIONS ENDPOINTS =====

@router.get("/{product_id}/units", response_model=List[schemas.ProductUnitRead])
def get_product_units(product_id: int, db: Session = Depends(get_db)):
    """Get all units/presentations for a product"""
    units = db.query(models.ProductUnit).filter(
        models.ProductUnit.product_id == product_id,
        models.ProductUnit.is_active == True
    ).all()
    return units

@router.post("/{product_id}/units", response_model=schemas.ProductUnitRead)
def create_product_unit(product_id: int, unit: schemas.ProductUnitCreate, db: Session = Depends(get_db)):
    """Create a new product unit/presentation"""
    # Verify product exists
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db_unit = models.ProductUnit(**unit.dict())
    db_unit.product_id = product_id  # Override with path param
    db.add(db_unit)
    db.commit()
    db.refresh(db_unit)
    return db_unit

@router.delete("/units/{unit_id}")
def delete_product_unit(unit_id: int, db: Session = Depends(get_db)):
    """Delete a product unit/presentation"""
    unit = db.query(models.ProductUnit).filter(models.ProductUnit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    
    # Soft delete
    unit.is_active = False
    db.commit()
    return {"status": "success"}
