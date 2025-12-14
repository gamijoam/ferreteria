from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from ..database.db import get_db
from ..models import models
from .. import schemas
import datetime

router = APIRouter(
    prefix="/cash",
    tags=["cash"]
)

@router.post("/open", response_model=schemas.CashSessionRead)
def open_session(session_data: schemas.CashSessionCreate, db: Session = Depends(get_db)):
    # Check if there's already an open session
    existing = db.query(models.CashSession).filter(
        models.CashSession.status == "OPEN"
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe una sesión de caja abierta")
    
    new_session = models.CashSession(
        user_id=1,  # Default user, since schema doesn't have user_id
        initial_cash=session_data.initial_cash,
        initial_cash_bs=session_data.initial_cash_bs,
        status="OPEN"
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

@router.get("/current/{user_id}", response_model=schemas.CashSessionRead)
def get_current_session(user_id: int, db: Session = Depends(get_db)):
    active = db.query(models.CashSession).filter(
        models.CashSession.user_id == user_id,
        models.CashSession.status == "OPEN"
    ).first()
    
    if not active:
        raise HTTPException(status_code=404, detail="No active session found")
        
    return active

@router.post("/{session_id}/close", response_model=schemas.CashSessionCloseResponse)
def close_session(session_id: int, close_data: schemas.CashSessionClose, db: Session = Depends(get_db)):
    session = db.query(models.CashSession).filter(models.CashSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    if session.status != "OPEN":
        raise HTTPException(status_code=400, detail="Session is not open")
    
    try:
        # --- Calculate Totals ---
        
        # 1. Sales by Method
        # 1. Sales by Method (Refactored to check SalePayment)
        sales_query = db.query(
            models.SalePayment.payment_method,
            models.SalePayment.currency,
            func.sum(models.SalePayment.amount)
        ).join(models.Sale).filter(models.Sale.date >= session.start_time).group_by(models.SalePayment.payment_method, models.SalePayment.currency).all()
        
        sales_by_method = {}
        sales_total_usd_eq = 0.0
        
        # Mocking exchange rate for reporting if needed, ideally fetched from DB
        try:
            current_exchange_rate = db.query(models.PriceRule).filter(models.PriceRule.name == "exchange_rate").first()
            rate = float(current_exchange_rate.value) if current_exchange_rate and current_exchange_rate.value else 40.0
        except Exception:
            rate = 40.0 # Safe fallback

        sales_usd_cash = 0.0
        sales_bs_cash = 0.0

        for method, currency, amount in sales_query:
            # Safer key generation
            method_str = str(method) if method else "Desconocido"
            currency_str = str(currency) if currency else "USD"
            key = f"{method_str} ({currency_str})"
            
            # Ensure amount is float
            val = float(amount) if amount else 0.0
            sales_by_method[key] = val
            
            # Add to total USD eq
            if currency_str == "USD":
                sales_total_usd_eq += val
                if "Efectivo" in method_str:
                    sales_usd_cash += val
            elif currency_str == "Bs":
                sales_total_usd_eq += (val / rate) if rate else 0
                if "Efectivo" in method_str:
                    sales_bs_cash += val

        # 2. Movements
        movements = db.query(models.CashMovement).filter(models.CashMovement.session_id == session.id).all()
        print(f"DEBUG: Found {len(movements)} movements for session {session.id}")
        for m in movements:
            print(f"  - Mov: {m.type} {m.currency} {m.amount}")
        
        expenses_usd = sum(m.amount for m in movements if m.type in ["OUT", "EXPENSE"] and m.currency == "USD")
        expenses_bs = sum(m.amount for m in movements if m.type in ["OUT", "EXPENSE"] and m.currency == "Bs")
        deposits_usd = sum(m.amount for m in movements if m.type in ["IN", "DEPOSIT"] and m.currency == "USD")
        deposits_bs = sum(m.amount for m in movements if m.type in ["IN", "DEPOSIT"] and m.currency == "Bs")

        # 3. Expected Cash
        expected_usd = session.initial_cash + sales_usd_cash + deposits_usd - expenses_usd
        expected_bs = session.initial_cash_bs + sales_bs_cash + deposits_bs - expenses_bs

        # Calculate Diffs
        diff_usd = close_data.final_cash_reported - expected_usd
        diff_bs = close_data.final_cash_reported_bs - expected_bs

        # Update Session
        session.end_time = datetime.datetime.now()
        session.status = "CLOSED"
        session.final_cash_reported = close_data.final_cash_reported
        session.final_cash_reported_bs = close_data.final_cash_reported_bs
        session.final_cash_expected = expected_usd
        session.final_cash_expected_bs = expected_bs
        session.difference = diff_usd
        session.difference_bs = diff_bs
        
        db.commit()
        db.refresh(session)
        
        return {
            "session": session,
            "expected_usd": expected_usd,
            "expected_bs": expected_bs,
            "diff_usd": diff_usd,
            "diff_bs": diff_bs,
            "details": {
                "initial_usd": session.initial_cash,
                "initial_bs": session.initial_cash_bs,
                "sales_total": sales_total_usd_eq,
                "sales_by_method": sales_by_method,
                "expenses_usd": expenses_usd,
                "expenses_bs": expenses_bs,
                "deposits_usd": deposits_usd,
                "deposits_bs": deposits_bs
            }
        }
    except Exception as e:
        print(f"Error closing session: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.post("/movements", response_model=schemas.CashMovementRead)
def add_movement(movement: schemas.CashMovementCreate, db: Session = Depends(get_db)):
    # Find active session if not provided
    if not movement.session_id:
        # Simplification: Assume current user ID 1 or passed in header (Future: Auth)
        # For now, find ANY open session (Single terminal mode)
        session = db.query(models.CashSession).filter(models.CashSession.status == "OPEN").first()
        if not session:
            raise HTTPException(status_code=400, detail="No active session to add movement")
        movement.session_id = session.id
        
    new_movement = models.CashMovement(
        session_id=movement.session_id,
        amount=movement.amount,
        type=movement.type,
        currency=movement.currency,
        description=movement.description, 
        exchange_rate=1.0 # Default
    )
    db.add(new_movement)
    db.commit()
    db.refresh(new_movement)
    return new_movement
