from sqlalchemy.orm import Session
from sqlalchemy import func
from src.models.models import CashSession, CashMovement, Sale, SaleDetail
import datetime

class CashController:
    def __init__(self, db: Session):
        self.db = db

    def get_current_session(self):
        return self.db.query(CashSession).filter(CashSession.status == "OPEN").first()

    def open_session(self, initial_amount: float):
        if self.get_current_session():
            raise ValueError("Ya existe una caja abierta.")
        
        new_session = CashSession(initial_cash=initial_amount, status="OPEN")
        self.db.add(new_session)
        self.db.commit()
        return new_session

    def add_movement(self, type: str, amount: float, description: str):
        session = self.get_current_session()
        if not session:
            raise ValueError("No hay caja abierta.")
            
        movement = CashMovement(
            session_id=session.id,
            type=type,
            amount=amount,
            description=description
        )
        self.db.add(movement)
        self.db.commit()
        return movement

    def get_session_balance(self):
        session = self.get_current_session()
        if not session:
            return None
            
        # Sum Sales since session start
        # Note: Ideally we link Sales to Session ID directly, but for now we filter by time
        # A robust system links Sale -> Session. Let's assume time-based for simplicity in this iteration
        # or we can query Sales where date >= session.start_time
        
        sales_total = self.db.query(func.sum(Sale.total_amount))\
            .filter(Sale.date >= session.start_time)\
            .scalar() or 0.0
            
        # Sum Movements
        movements_out = self.db.query(func.sum(CashMovement.amount))\
            .filter(CashMovement.session_id == session.id, CashMovement.type.in_(["EXPENSE", "WITHDRAWAL"]))\
            .scalar() or 0.0
            
        movements_in = self.db.query(func.sum(CashMovement.amount))\
            .filter(CashMovement.session_id == session.id, CashMovement.type == "DEPOSIT")\
            .scalar() or 0.0
            
        expected = session.initial_cash + sales_total + movements_in - movements_out
        
        return {
            "initial": session.initial_cash,
            "sales": sales_total,
            "expenses": movements_out,
            "deposits": movements_in,
            "expected": expected
        }

    def close_session(self, reported_amount: float):
        session = self.get_current_session()
        if not session:
            raise ValueError("No hay caja abierta.")
            
        balance = self.get_session_balance()
        expected = balance["expected"]
        difference = reported_amount - expected
        
        session.final_cash_reported = reported_amount
        session.final_cash_expected = expected
        session.difference = difference
        session.end_time = datetime.datetime.utcnow()
        session.status = "CLOSED"
        
        self.db.commit()
        
        return {
            "expected": expected,
            "reported": reported_amount,
            "difference": difference,
            "details": balance
        }
