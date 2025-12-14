from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from ..database.db import get_db
from ..models import models
from .. import schemas
from datetime import datetime

router = APIRouter(
    prefix="/returns",
    tags=["returns"]
)

@router.get("/sales/search", response_model=List[schemas.SaleRead])
def search_sales(q: Optional[str] = None, limit: int = 50, db: Session = Depends(get_db)):
    """Search sales by ID or customer name"""
    query = db.query(models.Sale).options(joinedload(models.Sale.customer))
    
    if not q:
        # Return recent sales
        return query.order_by(models.Sale.date.desc()).limit(limit).all()
    
    # Try to parse as ID
    if q.isdigit():
        return query.filter(models.Sale.id == int(q)).all()
    
    # Search by customer name
    query = query.join(models.Customer, isouter=True).filter(
        models.Customer.name.ilike(f"%{q}%")
    )
    
    return query.order_by(models.Sale.date.desc()).limit(limit).all()

@router.get("/sales/{sale_id}")
def get_sale_for_return(sale_id: int, db: Session = Depends(get_db)):
    """Get sale details for processing return"""
    sale = db.query(models.Sale).options(
        joinedload(models.Sale.details).joinedload(models.SaleDetail.product),
        joinedload(models.Sale.customer)
    ).filter(models.Sale.id == sale_id).first()
    
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    
    return sale

@router.post("/", response_model=schemas.ReturnRead)
def process_return(return_data: schemas.ReturnCreate, db: Session = Depends(get_db)):
    """Process a return: restore stock, create kardex entries, register cash movement"""
    
    # Find sale
    sale = db.query(models.Sale).filter(models.Sale.id == return_data.sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    
    # Create Return Record
    new_return = models.Return(
        sale_id=sale.id,
        total_refunded=0,  # Will update later
        reason=return_data.reason
    )
    db.add(new_return)
    db.flush()  # Get ID
    
    total_refund = 0
    
    for item in return_data.items:
        if item.quantity <= 0:
            continue
        
        # Find original sale detail
        detail = db.query(models.SaleDetail).filter(
            models.SaleDetail.sale_id == sale.id,
            models.SaleDetail.product_id == item.product_id
        ).first()
        
        if not detail:
            raise HTTPException(
                status_code=400,
                detail=f"Product {item.product_id} not found in this sale"
            )
        
        # Validation: Cannot return more than sold
        if item.quantity > detail.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot return more than purchased ({detail.quantity})"
            )
        
        # Calculate refund amount
        refund_amount = detail.unit_price * item.quantity
        total_refund += refund_amount
        
        # Create Return Detail
        ret_detail = models.ReturnDetail(
            return_id=new_return.id,
            product_id=item.product_id,
            quantity=item.quantity
        )
        db.add(ret_detail)
        
        # Restore Stock
        product = db.query(models.Product).get(item.product_id)
        product.stock += item.quantity
        
        # Kardex Entry
        kardex = models.Kardex(
            product_id=product.id,
            movement_type="RETURN",
            quantity=item.quantity,
            balance_after=product.stock,
            description=f"Devolución Venta #{sale.id}",
            date=datetime.now()
        )
        db.add(kardex)
    
    new_return.total_refunded = total_refund
    
    # Cash Impact (Refund)
    session = db.query(models.CashSession).filter(models.CashSession.status == "OPEN").first()
    if session:
        amount_to_record = total_refund
        if return_data.refund_currency == "Bs":
            amount_to_record = total_refund * return_data.exchange_rate
        
        cash_movement = models.CashMovement(
            session_id=session.id,
            type="EXPENSE",  # Refund is an expense
            amount=amount_to_record,
            currency=return_data.refund_currency,
            exchange_rate=return_data.exchange_rate,
            description=f"Devolución Venta #{sale.id}: {return_data.reason}"
        )
        db.add(cash_movement)
    
    db.commit()
    db.refresh(new_return)
    
    return new_return

@router.get("/", response_model=List[schemas.ReturnRead])
def get_returns(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get list of returns"""
    return db.query(models.Return).options(
        joinedload(models.Return.details).joinedload(models.ReturnDetail.product)
    ).order_by(models.Return.date.desc()).offset(skip).limit(limit).all()

@router.get("/{return_id}", response_model=schemas.ReturnRead)
def get_return(return_id: int, db: Session = Depends(get_db)):
    """Get specific return details"""
    ret = db.query(models.Return).options(
        joinedload(models.Return.details).joinedload(models.ReturnDetail.product)
    ).filter(models.Return.id == return_id).first()
    
    if not ret:
        raise HTTPException(status_code=404, detail="Return not found")
    
    return ret
