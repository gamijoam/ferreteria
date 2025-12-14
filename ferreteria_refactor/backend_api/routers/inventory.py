from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database.db import get_db
from ..models import models
from .. import schemas
from datetime import datetime

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"]
)

@router.post("/add")
def add_stock(adjustment: schemas.StockAdjustmentCreate, db: Session = Depends(get_db)):
    """Add stock (Purchase)"""
    product = db.query(models.Product).filter(models.Product.id == adjustment.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Calculation
    total_units = adjustment.quantity
    description = adjustment.description
    
    if adjustment.is_box_input and product.is_box:
        total_units = adjustment.quantity * product.conversion_factor
        description += f" (Entrada: {adjustment.quantity} Cajas x {product.conversion_factor})"
    else:
        description += f" (Entrada: {adjustment.quantity} Unidades)"

    # Update Stock
    product.stock += total_units
    
    # Create Kardex
    kardex_entry = models.Kardex(
        product_id=product.id,
        movement_type="PURCHASE", # Or adjustment.movement_type if generic
        quantity=total_units,
        balance_after=product.stock,
        description=description,
        date=datetime.now()
    )
    
    db.add(kardex_entry)
    db.commit()
    db.refresh(product)
    
    # Return updated product? Or success message. 
    # Let's return the product to update UI cache.
    # We need to map to ProductRead, so ensure router handles it.
    return {"status": "success", "new_stock": product.stock, "product_id": product.id}

@router.post("/remove")
def remove_stock(adjustment: schemas.StockAdjustmentCreate, db: Session = Depends(get_db)):
    """Remove stock (Adjustment/Loss)"""
    product = db.query(models.Product).filter(models.Product.id == adjustment.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.stock < adjustment.quantity:
        raise HTTPException(status_code=400, detail=f"Insufficient stock. Current: {product.stock}")

    # Update Stock
    product.stock -= adjustment.quantity # Assumes adjustment.quantity is already in UNITS if logic follows controller
    # Controller remove_stock took quantity (float).
    
    # Create Kardex
    kardex_entry = models.Kardex(
        product_id=product.id,
        movement_type="ADJUSTMENT_OUT",
        quantity=adjustment.quantity,
        balance_after=product.stock,
        description=adjustment.description,
        date=datetime.now()
    )
    
    db.add(kardex_entry)
    db.commit()
    db.refresh(product)
    
    return {"status": "success", "new_stock": product.stock, "product_id": product.id}

@router.get("/kardex", response_model=List[schemas.KardexRead])
def get_kardex(product_id: Optional[int] = None, limit: int = 100, db: Session = Depends(get_db)):
    from sqlalchemy.orm import joinedload
    query = db.query(models.Kardex).options(joinedload(models.Kardex.product))
    if product_id:
        query = query.filter(models.Kardex.product_id == product_id)
    return query.order_by(models.Kardex.date.desc()).limit(limit).all()
