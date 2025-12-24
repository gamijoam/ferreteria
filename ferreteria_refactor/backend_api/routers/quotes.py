from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database.db import get_db
from ..models import models
from .. import schemas

router = APIRouter(
    prefix="/quotes",
    tags=["quotes"]
)

@router.post("", response_model=schemas.QuoteRead)
def create_quote(quote_data: schemas.QuoteCreate, db: Session = Depends(get_db)):
    # Create Header
    new_quote = models.Quote(
        customer_id=quote_data.customer_id,
        total_amount=quote_data.total_amount,
        notes=quote_data.notes
    )
    db.add(new_quote)
    db.flush()

    # Create Details
    for item in quote_data.items:
        detail = models.QuoteDetail(
            quote_id=new_quote.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            subtotal=item.subtotal,
            is_box_sale=item.is_box
        )
        db.add(detail)
    
    db.commit()
    db.refresh(new_quote)
    # Return limited data compliant with schema
    # Pydantic will handle date conversion if models.date is datetime
    return new_quote

@router.get("", response_model=List[schemas.QuoteRead])
def read_quotes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Quote).order_by(models.Quote.date.desc()).offset(skip).limit(limit).all()



@router.get("/{quote_id}", response_model=schemas.QuoteReadWithDetails)
def read_quote_details(quote_id: int, db: Session = Depends(get_db)):
    quote = db.query(models.Quote).filter(models.Quote.id == quote_id).first()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    return quote

@router.put("/{quote_id}/convert")
def mark_quote_converted(quote_id: int, db: Session = Depends(get_db)):
    quote = db.query(models.Quote).filter(models.Quote.id == quote_id).first()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    quote.status = "CONVERTED"
    db.commit()
    return {"status": "success", "message": "Quote converted to sale"}
