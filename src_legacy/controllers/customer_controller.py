from sqlalchemy.orm import Session
from sqlalchemy import func
from src.models.models import Customer, Sale, Payment, CashSession, CashMovement
from src.utils.event_bus import event_bus

class CustomerController:
    def __init__(self, db: Session):
        self.db = db

    def create_customer(self, name: str, id_number: str = None, phone: str = "", address: str = ""):
        if not name:
            raise ValueError("El nombre es obligatorio")
            
        customer = Customer(name=name, id_number=id_number, phone=phone, address=address)
        self.db.add(customer)
        self.db.commit()
        event_bus.customers_updated.emit()
        return customer

    def get_all_customers(self):
        return self.db.query(Customer).all()

    def search_customers(self, query: str):
        """Search customers by name or ID number"""
        if not query:
            return self.get_all_customers()
            
        search = f"%{query}%"
        return self.db.query(Customer).filter(
            (Customer.name.ilike(search)) | 
            (Customer.id_number.ilike(search))
        ).all()

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

    def record_payment(self, customer_id: int, amount: float, description: str = "Abono a cuenta", payment_method: str = "Efectivo"):
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
            description=description,
            payment_method=payment_method
        )
        self.db.add(payment)
        
        # Add to cash
        cash_movement = CashMovement(
            session_id=session.id,
            type="DEPOSIT",
            amount=amount,
            description=f"Pago de cliente ({payment_method}): {description}"
        )
        self.db.add(cash_movement)
        
        self.db.commit()
        event_bus.sales_updated.emit() # Updates cash/debt
        return payment

    def add_payment(self, customer_id: int, amount: float, description: str = "Abono a cuenta", payment_method: str = "Efectivo"):
        """Alias for record_payment to maintain compatibility"""
        return self.record_payment(customer_id, amount, description, payment_method)

    def update_customer(self, customer_id: int, name: str, id_number: str = None, phone: str = "", address: str = ""):
        customer = self.db.query(Customer).get(customer_id)
        if not customer:
            raise ValueError("Cliente no encontrado")
        
        if not name:
            raise ValueError("El nombre es obligatorio")

        customer.name = name
        customer.id_number = id_number
        customer.phone = phone
        customer.address = address
        
        self.db.commit()
        event_bus.customers_updated.emit()
        return customer

    def delete_customer(self, customer_id: int):
        customer = self.db.query(Customer).get(customer_id)
        if not customer:
            raise ValueError("Cliente no encontrado")
            
        # Check for dependencies
        has_sales = self.db.query(Sale).filter(Sale.customer_id == customer_id).first()
        if has_sales:
            raise ValueError("No se puede eliminar el cliente porque tiene ventas asociadas.")
            
        has_payments = self.db.query(Payment).filter(Payment.customer_id == customer_id).first()
        if has_payments:
            raise ValueError("No se puede eliminar el cliente porque tiene pagos asociados.")

        self.db.delete(customer)
        self.db.commit()
        event_bus.customers_updated.emit()
        return True
