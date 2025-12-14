from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from ..database.db import get_db
from ..models import models
from .. import schemas
from datetime import datetime

router = APIRouter(
    prefix="/purchases",
    tags=["purchases"]
)

@router.post("/", response_model=schemas.PurchaseOrderRead)
def create_purchase_order(order_data: schemas.PurchaseOrderCreate, db: Session = Depends(get_db)):
    """Create a new purchase order"""
    try:
        # Calculate total
        total = sum(item.quantity * item.unit_cost for item in order_data.items)
        
        # Create order
        order = models.PurchaseOrder(
            supplier_id=order_data.supplier_id,
            total_amount=total,
            expected_delivery=order_data.expected_delivery,
            notes=order_data.notes
        )
        db.add(order)
        db.flush()  # Get order ID
        
        # Create details
        for item in order_data.items:
            detail = models.PurchaseOrderDetail(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_cost=item.unit_cost,
                subtotal=item.quantity * item.unit_cost
            )
            db.add(detail)
        
        db.commit()
        db.refresh(order)
        return order
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[schemas.PurchaseOrderRead])
def get_all_purchase_orders(status: Optional[str] = None, db: Session = Depends(get_db)):
    """Get all purchase orders, optionally filtered by status"""
    query = db.query(models.PurchaseOrder).options(
        joinedload(models.PurchaseOrder.supplier),
        joinedload(models.PurchaseOrder.details).joinedload(models.PurchaseOrderDetail.product)
    )
    
    if status:
        query = query.filter(models.PurchaseOrder.status == status)
    
    return query.order_by(models.PurchaseOrder.order_date.desc()).all()

@router.get("/{order_id}", response_model=schemas.PurchaseOrderRead)
def get_purchase_order(order_id: int, db: Session = Depends(get_db)):
    """Get purchase order by ID"""
    order = db.query(models.PurchaseOrder).options(
        joinedload(models.PurchaseOrder.supplier),
        joinedload(models.PurchaseOrder.details).joinedload(models.PurchaseOrderDetail.product)
    ).filter(models.PurchaseOrder.id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    
    return order

@router.post("/{order_id}/receive", response_model=schemas.PurchaseOrderRead)
def receive_purchase_order(order_id: int, receive_data: schemas.PurchaseOrderReceive, db: Session = Depends(get_db)):
    """
    Receive a purchase order:
    - Update product stock
    - Update product cost_price
    - Create Kardex entries
    - Mark order as RECEIVED
    """
    order = db.query(models.PurchaseOrder).filter(models.PurchaseOrder.id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    
    if order.status != "PENDING":
        raise HTTPException(status_code=400, detail=f"Order is already {order.status}")
    
    try:
        for detail in order.details:
            product = db.query(models.Product).get(detail.product_id)
            if not product:
                continue
            
            # Update stock
            old_stock = product.stock
            product.stock += detail.quantity
            
            # Update cost_price with weighted average
            if product.cost_price == 0:
                product.cost_price = detail.unit_cost
            else:
                total_value = (product.cost_price * old_stock) + (detail.unit_cost * detail.quantity)
                product.cost_price = total_value / product.stock
            
            # Create Kardex entry
            supplier = db.query(models.Supplier).get(order.supplier_id)
            kardex = models.Kardex(
                product_id=product.id,
                movement_type="PURCHASE",
                quantity=detail.quantity,
                balance_after=product.stock,
                description=f"Recepción OC #{order.id} - {supplier.name if supplier else 'N/A'}",
                date=datetime.now()
            )
            db.add(kardex)
        
        # Mark order as received
        order.status = "RECEIVED"
        order.received_date = datetime.now()
        order.received_by = receive_data.user_id
        
        db.commit()
        db.refresh(order)
        return order
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{order_id}")
def cancel_purchase_order(order_id: int, db: Session = Depends(get_db)):
    """Cancel a purchase order"""
    order = db.query(models.PurchaseOrder).filter(models.PurchaseOrder.id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    
    if order.status == "RECEIVED":
        raise HTTPException(status_code=400, detail="Cannot cancel a received order")
    
    try:
        order.status = "CANCELLED"
        db.commit()
        return {"message": "Order cancelled successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
