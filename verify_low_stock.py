from src.database.db import SessionLocal
from src.controllers.product_controller import ProductController
from src.models.models import Product
import datetime

def verify_low_stock():
    db = SessionLocal()
    controller = ProductController(db)
    
    print("=== VERIFICACIÓN DE ALERTAS DE STOCK ===")
    
    # 1. Crear producto con stock bajo
    test_sku = f"ALERT-{datetime.datetime.now().timestamp()}"
    print(f"Creando producto con Stock 3.0 y Min Stock 5.0...")
    
    product = controller.create_product(
        name=f"Producto Alerta {datetime.datetime.now().strftime('%H:%M:%S')}",
        sku=test_sku,
        price=100.0,
        cost_price=50.0,
        stock=3.0,
        min_stock=5.0,
        is_box=False,
        conversion_factor=1,
        unit_type="Unidad"
    )
    
    print(f"Producto creado: {product.name} (ID: {product.id})")
    print(f"Stock: {product.stock} | Min Stock: {product.min_stock}")
    
    # Verificar lógica de alerta (simulada, ya que la alerta visual está en la UI)
    if product.stock <= product.min_stock:
        print("✅ ALERTA ACTIVADA: Stock actual es menor o igual al mínimo.")
    else:
        print("❌ ERROR: No se detectó condición de alerta.")
        
    # 2. Actualizar stock para quitar alerta
    print("\nActualizando stock a 10.0...")
    controller.update_product(
        product_id=product.id,
        name=product.name,
        sku=product.sku,
        price=product.price,
        cost_price=product.cost_price,
        stock=10.0,
        min_stock=5.0,
        is_box=False,
        conversion_factor=1,
        unit_type="Unidad"
    )
    
    db.refresh(product)
    print(f"Nuevo Stock: {product.stock}")
    
    if product.stock > product.min_stock:
        print("✅ ALERTA DESACTIVADA: Stock actual es mayor al mínimo.")
    else:
        print("❌ ERROR: La condición de alerta persiste incorrectamente.")

    db.close()

if __name__ == "__main__":
    verify_low_stock()
