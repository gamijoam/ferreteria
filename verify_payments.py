from src.database.db import SessionLocal
from src.controllers.cash_controller import CashController
from src.controllers.pos_controller import POSController
from src.models.models import Product
import datetime

def verify_payments():
    db = SessionLocal()
    cash_ctrl = CashController(db)
    pos_ctrl = POSController(db)
    
    print("=== VERIFICACIÓN DE MÉTODOS DE PAGO ===")
    
    # 1. Asegurar que no hay caja abierta (cerrar si existe)
    session = cash_ctrl.get_current_session()
    if session:
        print("Cerrando sesión anterior...")
        cash_ctrl.close_session(session.initial_cash) # Cierre ficticio
        
    # 2. Abrir Caja con $1000
    print("\nAbriendo caja con $1000...")
    cash_ctrl.open_session(1000.0)
    
    # 3. Crear producto de prueba
    test_sku = f"PAY-{datetime.datetime.now().timestamp()}"
    product = Product(
        name="Producto Pago Test",
        sku=test_sku,
        price=100.0,
        stock=100.0,
        unit_type="Unidad"
    )
    db.add(product)
    db.commit()
    
    # 4. Venta 1: Efectivo ($100)
    print("\nRealizando Venta 1: $100 (Efectivo)...")
    pos_ctrl.add_to_cart(test_sku, 1, False)
    success, msg, _ = pos_ctrl.finalize_sale(payment_method="Efectivo")
    if success: print("Venta Efectivo OK")
    else: print(f"Error Venta Efectivo: {msg}")
    
    # 5. Venta 2: Transferencia ($200)
    print("\nRealizando Venta 2: $200 (Transferencia)...")
    pos_ctrl.add_to_cart(test_sku, 2, False)
    success, msg, _ = pos_ctrl.finalize_sale(payment_method="Transferencia")
    if success: print("Venta Transferencia OK")
    else: print(f"Error Venta Transferencia: {msg}")
    
    # 6. Consultar Balance antes de cerrar
    balance = cash_ctrl.get_session_balance()
    print("\n--- Balance Previsto ---")
    print(f"Ventas Totales: ${balance['sales_total']}")
    print(f"Desglose: {balance['sales_by_method']}")
    print(f"Efectivo Esperado en Caja: ${balance['expected_cash']}")
    
    # Validaciones
    assert balance['sales_total'] == 300.0, "Total ventas incorrecto"
    assert balance['sales_by_method'].get('Efectivo') == 100.0, "Total efectivo incorrecto"
    assert balance['sales_by_method'].get('Transferencia') == 200.0, "Total transferencia incorrecto"
    assert balance['expected_cash'] == 1100.0, "Efectivo esperado incorrecto (1000 inicial + 100 venta)"
    
    print("\nTODOS LOS CALCULOS SON CORRECTOS")
    
    # 7. Cerrar Caja
    print("\nCerrando caja reportando $1100...")
    result = cash_ctrl.close_session(1100.0)
    print(f"Diferencia: {result['difference']}")
    
    db.close()

if __name__ == "__main__":
    verify_payments()
