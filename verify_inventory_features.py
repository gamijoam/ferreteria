from src.database.db import SessionLocal
from src.controllers.inventory_controller import InventoryController
from src.models.models import Product, MovementType
import datetime

def verify_inventory():
    db = SessionLocal()
    controller = InventoryController(db)
    
    print("=== VERIFICACIÓN DE INVENTARIO ===")
    
    # 1. Crear producto de prueba
    test_sku = f"TEST-{datetime.datetime.now().timestamp()}"
    product = Product(
        name=f"Producto Test {datetime.datetime.now().strftime('%H:%M:%S')}",
        sku=test_sku,
        price=10.0,
        stock=100.0,
        unit_type="Unidad"
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    print(f"Producto creado: {product.name} (ID: {product.id}, Stock: {product.stock})")
    
    # 2. Probar Salida de Stock
    print("\n--- Probando Salida de Stock ---")
    try:
        updated_product = controller.remove_stock(product.id, 5.5, "Donación de prueba")
        print(f"Stock después de salida (5.5): {updated_product.stock}")
        assert updated_product.stock == 94.5, "El stock no se actualizó correctamente"
    except Exception as e:
        print(f"ERROR en salida de stock: {e}")
        
    # 3. Probar Historial (Kardex)
    print("\n--- Probando Historial (Kardex) ---")
    
    # Historial específico
    kardex_specific = controller.get_kardex(product.id)
    print(f"Registros para producto {product.id}: {len(kardex_specific)}")
    for k in kardex_specific:
        print(f"  - {k.date}: {k.movement_type.value} | Cant: {k.quantity} | Saldo: {k.balance_after} | Desc: {k.description}")
        
    # Historial completo (None)
    print("\n--- Probando Historial Completo (Todos) ---")
    kardex_all = controller.get_kardex(None)
    print(f"Total registros en historial: {len(kardex_all)}")
    
    # Verificar que nuestro movimiento está ahí
    found = False
    for k in kardex_all:
        if k.product_id == product.id and k.movement_type == MovementType.ADJUSTMENT_OUT:
            print(f"  ✓ Encontrado movimiento de salida en historial general: {k.description}")
            found = True
            break
            
    if not found:
        print("  ❌ NO se encontró el movimiento en el historial general")
        
    db.close()

if __name__ == "__main__":
    verify_inventory()
