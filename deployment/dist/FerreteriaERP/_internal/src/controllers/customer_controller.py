from sqlalchemy.orm import Session
from sqlalchemy import func
from src.models.models import Customer, Sale, Payment, CashSession, CashMovement

class CustomerController:
    def __init__(self, db: Session):
        self.db = db

    def create_customer(self, name: str, phone: str = "", address: str = ""):
        if not name:
            raise ValueError("El nombre es obligatorio")
            
        customer = Customer(name=name, phone=phone, address=address)
        self.db.add(customer)
        self.db.commit()
        return customer

    def get_all_customers(self):
        return self.db.query(Customer).all()

    def get_customer_debt(self, customer_id: int):
        """Calculate total debt: unpaid sales - payments"""
        # Sum of unpaid sales
        unpaid_sales = self.db.query(func.sum(Sale.total_amount)).filter(
            Sale.customer_id == customer_id,
            Sale.is_credit == True,
            Sale.paid == False
        ).scalar() or 0.0
        
        # Sum of payments
        payments = self.db.query(func.sum(Payment.amount)).filter(
            Payment.customer_id == customer_id
        ).scalar() or 0.0
        
        return unpaid_sales - payments

    def record_payment(self, customer_id: int, amount: float, description: str = "Abono a cuenta"):
        if amount <= 0:
            raise ValueError("El monto debe ser mayor a 0")
        
        # Check if cash session is open
        session = self.db.query(CashSession).filter(CashSession.status == "OPEN").first()
        if not session:
            raise ValueError("Debe abrir una sesión de caja antes de registrar pagos")
            
        # Create payment record
        payment = Payment(
            customer_id=customer_id,
            amount=amount,
            description=description
        )
        self.db.add(payment)
        
        # Add to cash
        cash_movement = CashMovement(
            session_id=session.id,
            type="DEPOSIT",
            amount=amount,
            description=f"Pago de cliente: {description}"
        )
        self.db.add(cash_movement)
        
        self.db.commit()
        return payment
