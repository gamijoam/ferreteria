from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database.db import get_db
from ..models import models
from ..schemas import ProductRead, SaleCreate

router = APIRouter(prefix="/api/v1/products", tags=["products"])

@router.get("/", response_model=List[ProductRead])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = db.query(models.Product).filter(models.Product.is_active == True).offset(skip).limit(limit).all()
    return products

@router.post("/sales/")
def create_sale(sale_data: SaleCreate, db: Session = Depends(get_db)):
    # 1. Create Sale Header
    new_sale = models.Sale(
        total_amount=sale_data.total_amount,
        payment_method=sale_data.payment_method,
        customer_id=sale_data.customer_id,
        is_credit=False, # logic simplified for example
        paid=True
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
        subtotal = price_used * item.quantity
        
        detail = models.SaleDetail(
            sale_id=new_sale.id,
            product_id=product.id,
            quantity=units_to_deduct, # Deduct base units
            unit_price=product.price, # Store base unit price
            subtotal=subtotal,
            is_box_sale=item.is_box
        )
        db.add(detail)

        # Update Stock
        product.stock -= units_to_deduct

    db.commit()
    return {"status": "success", "sale_id": new_sale.id}
