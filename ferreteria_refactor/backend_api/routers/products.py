from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database.db import get_db
from ..models import models
from .. import schemas

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_model=List[schemas.ProductRead])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = db.query(models.Product).filter(models.Product.is_active == True).offset(skip).limit(limit).all()
    return products

@router.post("/", response_model=schemas.ProductRead)
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
