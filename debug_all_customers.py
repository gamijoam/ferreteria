"""
Script para diagnosticar el problema de cálculo de deuda - TODOS LOS CLIENTES
"""
from src.database.db import SessionLocal
from src.controllers.customer_controller import CustomerController
from sqlalchemy import func
from src.models.models import Customer, Sale, Payment

db = SessionLocal()
controller = CustomerController(db)

# Listar todos los clientes
print("=== TODOS LOS CLIENTES ===\n")
customers = controller.get_all_customers()

for customer in customers:
    print(f"{'='*60}")
    print(f"CLIENTE: {customer.name} (ID: {customer.id})")
    print(f"{'='*60}")
    
    # Ventas a crédito no pagadas
    unpaid_sales = db.query(Sale).filter(
        Sale.customer_id == customer.id,
        Sale.is_credit == True,
        Sale.paid == False
    ).all()
    
    print(f"\nVentas a crédito no pagadas: {len(unpaid_sales)}")
    total_unpaid = 0
    for sale in unpaid_sales:
        print(f"  - Venta ID {sale.id}: ${sale.total_amount:.2f}")
        total_unpaid += sale.total_amount
    print(f"Total ventas: ${total_unpaid:.2f}")
    
    # Pagos
    payments = db.query(Payment).filter(
        Payment.customer_id == customer.id
    ).all()
    
    print(f"\nPagos registrados: {len(payments)}")
    total_payments = 0
    for payment in payments:
        print(f"  - Pago ID {payment.id}: ${payment.amount:.2f} ({type(payment.amount).__name__}) - {payment.description}")
        total_payments += payment.amount
    print(f"Total pagos: ${total_payments:.2f}")
    
    # Deuda calculada
    debt = controller.get_customer_debt(customer.id)
    print(f"\nDeuda calculada: ${debt:.2f}")
    print(f"Deuda manual: ${total_unpaid:.2f} - ${total_payments:.2f} = ${total_unpaid - total_payments:.2f}")
    print()

db.close()
