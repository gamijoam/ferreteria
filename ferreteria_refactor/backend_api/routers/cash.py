from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from ..database.db import get_db
from ..models import models
from .. import schemas
import datetime
from ..websocket.manager import manager
from ..websocket.events import WebSocketEvents

router = APIRouter(
    prefix="/cash",
    tags=["cash"]
)

@router.post("/open", response_model=schemas.CashSessionRead)
async def open_session(session_data: schemas.CashSessionCreate, db: Session = Depends(get_db)):
    # Check if there's already an open session
    existing = db.query(models.CashSession).filter(
        models.CashSession.status == "OPEN"
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe una sesión de caja abierta")
    
    # Create session
    new_session = models.CashSession(
        user_id=1,  # Default user
        initial_cash=session_data.initial_cash,
        initial_cash_bs=session_data.initial_cash_bs,
        status="OPEN"
    )
    db.add(new_session)
    db.flush()  # Get session ID
    
    # Create currency records for each currency in the request
    for curr_data in session_data.currencies:
        currency_record = models.CashSessionCurrency(
            session_id=new_session.id,
            currency_symbol=curr_data.currency_symbol,
            initial_amount=curr_data.initial_amount
        )
        db.add(currency_record)
    
    db.commit()
    db.refresh(new_session)
    
    await manager.broadcast(WebSocketEvents.CASH_SESSION_OPENED, {
        "id": new_session.id, 
        "user_id": new_session.user_id,
        "status": "OPEN"
    })
    
    return new_session

@router.get("/active", response_model=schemas.CashSessionRead)
def get_active_session(db: Session = Depends(get_db)):
    """Get the currently open session (globally)"""
    active = db.query(models.CashSession).filter(
        models.CashSession.status == "OPEN"
    ).first()
    
    if not active:
        raise HTTPException(status_code=404, detail="No active session found")
        
    return active

@router.get("/active", response_model=schemas.CashSessionRead)
def get_active_session(db: Session = Depends(get_db)):
    """Get the currently open session (globally)"""
    active = db.query(models.CashSession).filter(
        models.CashSession.status == "OPEN"
    ).first()
    
    if not active:
        raise HTTPException(status_code=404, detail="No active session found")
        
    return active

@router.get("/current/{user_id}", response_model=schemas.CashSessionRead)
def get_current_session(user_id: int, db: Session = Depends(get_db)):
    active = db.query(models.CashSession).filter(
        models.CashSession.user_id == user_id,
        models.CashSession.status == "OPEN"
    ).first()
    
    if not active:
        raise HTTPException(status_code=404, detail="No active session found for user")
        
    return active

@router.get("/history", response_model=List[schemas.CashSessionRead])
def get_session_history(
    skip: int = 0, 
    limit: int = 20, 
    start_date: str = None,
    end_date: str = None,
    db: Session = Depends(get_db)
):
    """Get closed session history with date filtering"""
    from sqlalchemy.orm import joinedload
    query = db.query(models.CashSession).options(
        joinedload(models.CashSession.user),
        joinedload(models.CashSession.currencies)
    ).filter(
        models.CashSession.status == "CLOSED"
    )
    
    if start_date:
        # Assuming YYYY-MM-DD format
        try:
            start_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(models.CashSession.end_time >= start_dt)
        except ValueError:
            pass # Ignore invalid dates
            
    if end_date:
        try:
            end_dt = datetime.datetime.strptime(end_date, "%Y-%m-%d")
            # Set to end of day
            end_dt = end_dt.replace(hour=23, minute=59, second=59)
            query = query.filter(models.CashSession.end_time <= end_dt)
        except ValueError:
            pass

    sessions = query.order_by(models.CashSession.end_time.desc()).offset(skip).limit(limit).all()
    return sessions

def calculate_session_totals(session, db):
    """Helper to calculate session totals per currency, separating cash from transfers"""
    start_time = session.start_time
    end_time = session.end_time if session.end_time else datetime.datetime.now()
    
    # Get all sale payments in this time range
    sales_query = db.query(
        models.SalePayment.payment_method,
        models.SalePayment.currency,
        func.sum(models.SalePayment.amount)
    ).join(models.Sale).filter(
        models.Sale.date >= start_time,
        models.Sale.date <= end_time
    ).group_by(models.SalePayment.payment_method, models.SalePayment.currency).all()
    
    # Organize sales by currency and method
    cash_by_currency = {}  # {currency: amount} - only Efectivo
    transfers_by_currency = {}  # {currency: {method: amount}} - all other methods
    sales_by_method = {}  # For legacy display
    
    for method, currency, amount in sales_query:
        method_str = str(method) if method else "Desconocido"
        currency_str = str(currency) if currency else "USD"
        val = float(amount) if amount else 0.0
        
        # Track for legacy display
        key = f"{method_str} ({currency_str})"
        sales_by_method[key] = val
        
        # Separate cash from transfers
        if "Efectivo" in method_str:
            cash_by_currency[currency_str] = cash_by_currency.get(currency_str, 0) + val
        else:
            if currency_str not in transfers_by_currency:
                transfers_by_currency[currency_str] = {}
            transfers_by_currency[currency_str][method_str] = transfers_by_currency[currency_str].get(method_str, 0) + val
    
    # Get movements by currency
    movements = db.query(models.CashMovement).filter(models.CashMovement.session_id == session.id).all()
    
    movements_by_currency = {}
    for m in movements:
        curr = m.currency or "USD"
        if curr not in movements_by_currency:
            movements_by_currency[curr] = {"deposits": 0, "expenses": 0}
        
        if m.type in ["IN", "DEPOSIT"]:
            movements_by_currency[curr]["deposits"] += m.amount
        elif m.type in ["OUT", "EXPENSE"]:
            movements_by_currency[curr]["expenses"] += m.amount
    
    # Calculate expected per currency
    expected_by_currency = {}
    
    # Get session currencies
    session_currencies = db.query(models.CashSessionCurrency).filter(
        models.CashSessionCurrency.session_id == session.id
    ).all()
    
    for sess_curr in session_currencies:
        symbol = sess_curr.currency_symbol
        initial = sess_curr.initial_amount
        sales_cash = cash_by_currency.get(symbol, 0)
        deposits = movements_by_currency.get(symbol, {}).get("deposits", 0)
        expenses = movements_by_currency.get(symbol, {}).get("expenses", 0)
        
        expected = initial + sales_cash + deposits - expenses
        expected_by_currency[symbol] = expected
    
    # Legacy USD/Bs calculation for backward compatibility
    sales_usd_cash = cash_by_currency.get("USD", 0)
    sales_bs_cash = cash_by_currency.get("Bs", 0)
    expenses_usd = movements_by_currency.get("USD", {}).get("expenses", 0)
    expenses_bs = movements_by_currency.get("Bs", {}).get("expenses", 0)
    deposits_usd = movements_by_currency.get("USD", {}).get("deposits", 0)
    deposits_bs = movements_by_currency.get("Bs", {}).get("deposits", 0)
    
    expected_usd = session.initial_cash + sales_usd_cash + deposits_usd - expenses_usd
    expected_bs = session.initial_cash_bs + sales_bs_cash + deposits_bs - expenses_bs
    
    return {
        "expected_usd": expected_usd,
        "expected_bs": expected_bs,
        "expected_by_currency": expected_by_currency,
        "cash_by_currency": cash_by_currency,
        "transfers_by_currency": transfers_by_currency,
        "details": {
            "initial_usd": session.initial_cash,
            "initial_bs": session.initial_cash_bs,
            "sales_total": sum(cash_by_currency.values()),  # Total cash sales
            "sales_by_method": sales_by_method,
            "expenses_usd": expenses_usd,
            "expenses_bs": expenses_bs,
            "deposits_usd": deposits_usd,
            "deposits_bs": deposits_bs,
            "cash_by_currency": cash_by_currency,
            "transfers_by_currency": transfers_by_currency
        }
    }

@router.get("/history/{session_id}", response_model=schemas.CashSessionCloseResponse)
def get_session_details(session_id: int, db: Session = Depends(get_db)):
    """Get details of a closed session (recalculated)"""
    session = db.query(models.CashSession).filter(models.CashSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Calculate totals
    totals = calculate_session_totals(session, db)
    
    return {
        "session": session,
        "details": totals["details"],
        "expected_usd": totals["expected_usd"],
        "expected_bs": totals["expected_bs"],
        "expected_by_currency": totals.get("expected_by_currency", {}),
        "diff_usd": session.difference or 0.0,
        "diff_bs": session.difference_bs or 0.0,
        "diff_by_currency": {}  # Will be calculated on close
    }

@router.post("/{session_id}/close", response_model=schemas.CashSessionCloseResponse)
async def close_session(session_id: int, close_data: schemas.CashSessionClose, db: Session = Depends(get_db)):
    session = db.query(models.CashSession).filter(models.CashSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    if session.status != "OPEN":
        raise HTTPException(status_code=400, detail="Session is not open")
    
    try:
        # Calculate expected based on CURRENT time (closing now)
        totals = calculate_session_totals(session, db)
        expected_usd = totals["expected_usd"]
        expected_bs = totals["expected_bs"]
        expected_by_currency = totals.get("expected_by_currency", {})

        # ========================================
        # NEW: Calculate Total Sales vs Cash Collected
        # ========================================
        start_time = session.start_time
        end_time = datetime.datetime.now()
        
        # Total Sales (Facturado) - ALL sales including credit
        total_sales_invoiced = db.query(func.sum(models.Sale.total_amount)).filter(
            models.Sale.date >= start_time,
            models.Sale.date <= end_time
        ).scalar() or 0.0
        
        # Total Cash Collected (Recaudado) - Only from SalePayments
        total_cash_collected = db.query(func.sum(models.SalePayment.amount)).join(
            models.Sale
        ).filter(
            models.Sale.date >= start_time,
            models.Sale.date <= end_time,
            models.SalePayment.currency == "USD"  # Only USD for main total
        ).scalar() or 0.0

        # Calculate Diffs (legacy)
        diff_usd = close_data.final_cash_reported - expected_usd
        diff_bs = close_data.final_cash_reported_bs - expected_bs
        
        # Calculate and save per-currency differences
        diff_by_currency = {}
        print(f"🔍 DEBUG - Currencies received in close_data: {close_data.currencies}")
        print(f"🔍 DEBUG - Expected by currency: {expected_by_currency}")
        
        for curr_data in close_data.currencies:
            symbol = curr_data.get("symbol")
            reported = curr_data.get("amount", 0)
            expected = expected_by_currency.get(symbol, 0)
            diff = reported - expected
            diff_by_currency[symbol] = diff
            
            print(f"💰 {symbol}: Reported={reported}, Expected={expected}, Diff={diff}")
            
            # Update CashSessionCurrency record
            sess_curr = db.query(models.CashSessionCurrency).filter(
                models.CashSessionCurrency.session_id == session_id,
                models.CashSessionCurrency.currency_symbol == symbol
            ).first()
            
            if sess_curr:
                print(f"   📊 Session Currency: Initial={sess_curr.initial_amount}")
                sess_curr.final_reported = reported
                sess_curr.final_expected = expected
                sess_curr.difference = diff

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
            "expected_by_currency": expected_by_currency,
            "diff_by_currency": diff_by_currency,
            "details": totals["details"],
            # NEW: Separate totals for invoiced vs collected
            "total_sales_invoiced": round(total_sales_invoiced, 2),
            "total_cash_collected": round(total_cash_collected, 2)
        }
        
        await manager.broadcast(WebSocketEvents.CASH_SESSION_CLOSED, {
            "id": session.id,
            "user_id": session.user_id,
            "status": "CLOSED"
        })
        
        return response_data
    except Exception as e:
        print(f"Error closing session: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.post("/movements", response_model=schemas.CashMovementRead)
async def add_movement(movement: schemas.CashMovementCreate, db: Session = Depends(get_db)):
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
    db.refresh(new_movement)
    
    await manager.broadcast(WebSocketEvents.CASH_SESSION_MOVEMENT, {
        "id": new_movement.id,
        "session_id": new_movement.session_id,
        "amount": new_movement.amount,
        "type": new_movement.type
    })
    
    return new_movement

