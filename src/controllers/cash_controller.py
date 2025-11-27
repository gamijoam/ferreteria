from sqlalchemy.orm import Session
from sqlalchemy import func
from src.models.models import CashSession, CashMovement, Sale, SaleDetail
import datetime

class CashController:
    def __init__(self, db: Session):
        self.db = db

    def get_current_session(self):
        return self.db.query(CashSession).filter(CashSession.status == "OPEN").first()

    def open_session(self, initial_usd: float, initial_bs: float = 0.0):
        if self.get_current_session():
            raise ValueError("Ya existe una caja abierta.")
        
        new_session = CashSession(
            initial_cash=initial_usd, 
            initial_cash_bs=initial_bs,
            status="OPEN"
        )
        self.db.add(new_session)
        self.db.commit()
        return new_session

    def add_movement(self, type: str, amount: float, description: str, currency: str = "USD", exchange_rate: float = 1.0):
        session = self.get_current_session()
        if not session:
            raise ValueError("No hay caja abierta.")
            
        movement = CashMovement(
            session_id=session.id,
            type=type,
            amount=amount,
            currency=currency,
            exchange_rate=exchange_rate,
            description=description
        )
        self.db.add(movement)
        self.db.commit()
        return movement

    def get_session_balance(self):
        session = self.get_current_session()
        if not session:
            return None
            
        # 1. Sales Breakdown (USD and Bs)
        # We need to sum separately based on payment method
        
        # Query sales since session start
        sales = self.db.query(Sale).filter(Sale.date >= session.start_time).all()
        
        sales_by_method = {}
        sales_total_usd = 0.0
        
        cash_sales_usd = 0.0
        cash_sales_bs = 0.0
        
        for sale in sales:
            method = sale.payment_method
            sales_total_usd += sale.total_amount
            
            if method not in sales_by_method:
                sales_by_method[method] = 0.0
            sales_by_method[method] += sale.total_amount
            
            # Calculate Cash Sales
            if method == "Efectivo USD":
                cash_sales_usd += sale.total_amount
            elif method == "Efectivo Bs":
                # For Bs sales, we use the stored Bs amount
                # If total_amount_bs is None (legacy), convert using rate used
                amount_bs = sale.total_amount_bs if sale.total_amount_bs is not None else (sale.total_amount * sale.exchange_rate_used)
                cash_sales_bs += amount_bs

        # 2. Movements (Expenses/Deposits)
        movements = self.db.query(CashMovement).filter(CashMovement.session_id == session.id).all()
        
        expenses_usd = 0.0
        expenses_bs = 0.0
        deposits_usd = 0.0
        deposits_bs = 0.0
        
        for mov in movements:
            if mov.type in ["EXPENSE", "WITHDRAWAL"]:
                if mov.currency == "Bs":
                    expenses_bs += mov.amount
                else:
                    expenses_usd += mov.amount
            elif mov.type == "DEPOSIT":
                if mov.currency == "Bs":
                    deposits_bs += mov.amount
                else:
                    deposits_usd += mov.amount
            
        # 3. Calculate Expected Cash
        expected_usd = session.initial_cash + cash_sales_usd + deposits_usd - expenses_usd
        expected_bs = session.initial_cash_bs + cash_sales_bs + deposits_bs - expenses_bs
        
        return {
            "initial_usd": session.initial_cash,
            "initial_bs": session.initial_cash_bs,
            "sales_total": sales_total_usd,
            "sales_by_method": sales_by_method,
            "expenses_usd": expenses_usd,
            "expenses_bs": expenses_bs,
            "deposits_usd": deposits_usd,
            "deposits_bs": deposits_bs,
            "expected_usd": expected_usd,
            "expected_bs": expected_bs
        }

    def close_session(self, reported_usd: float, reported_bs: float):
        session = self.get_current_session()
        if not session:
            raise ValueError("No hay caja abierta.")
            
        balance = self.get_session_balance()
        expected_usd = balance["expected_usd"]
        expected_bs = balance["expected_bs"]
        
        diff_usd = reported_usd - expected_usd
        diff_bs = reported_bs - expected_bs
        
        session.final_cash_reported = reported_usd
        session.final_cash_reported_bs = reported_bs
        session.final_cash_expected = expected_usd
        session.final_cash_expected_bs = expected_bs
        session.difference = diff_usd
        session.difference_bs = diff_bs
        
        session.end_time = datetime.datetime.utcnow()
        session.status = "CLOSED"
        
        self.db.commit()
        
        return {
            "expected_usd": expected_usd,
            "expected_bs": expected_bs,
            "reported_usd": reported_usd,
            "reported_bs": reported_bs,
            "diff_usd": diff_usd,
            "diff_bs": diff_bs,
            "details": balance
        }
