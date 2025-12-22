"""
Script para verificar el estado de la base de datos después de las migraciones
"""
import sys
sys.path.insert(0, 'c:/Users/Equipo/Documents/ferreteria')

from ferreteria_refactor.backend_api.database import SessionLocal
from ferreteria_refactor.backend_api.models.models import Product, ProductUnit
from sqlalchemy import inspect

def check_database():
    db = SessionLocal()
    try:
        # Check Product table columns
        print("=" * 60)
        print("CHECKING PRODUCT TABLE")
        print("=" * 60)
        inspector = inspect(db.bind)
        product_columns = [col['name'] for col in inspector.get_columns('products')]
        print(f"Product columns: {product_columns}")
        
        required_product_fields = ['profit_margin', 'discount_percentage', 'is_discount_active']
        for field in required_product_fields:
            if field in product_columns:
                print(f"✅ {field} exists in products table")
            else:
                print(f"❌ {field} MISSING in products table")
        
        # Check ProductUnit table columns
        print("\n" + "=" * 60)
        print("CHECKING PRODUCT_UNITS TABLE")
        print("=" * 60)
        unit_columns = [col['name'] for col in inspector.get_columns('product_units')]
        print(f"ProductUnit columns: {unit_columns}")
        
        required_unit_fields = ['cost_price', 'profit_margin', 'discount_percentage', 'is_discount_active']
        for field in required_unit_fields:
            if field in unit_columns:
                print(f"✅ {field} exists in product_units table")
            else:
                print(f"❌ {field} MISSING in product_units table")
        
        # Try to query products
        print("\n" + "=" * 60)
        print("TESTING PRODUCT QUERY")
        print("=" * 60)
        try:
            products = db.query(Product).limit(5).all()
            print(f"✅ Successfully queried {len(products)} products")
            
            for product in products:
                print(f"\nProduct: {product.name}")
                print(f"  - profit_margin: {product.profit_margin}")
                print(f"  - discount_percentage: {product.discount_percentage}")
                print(f"  - is_discount_active: {product.is_discount_active}")
                print(f"  - units count: {len(product.units)}")
                
                for unit in product.units[:2]:  # First 2 units
                    print(f"    Unit: {unit.unit_name}")
                    print(f"      - cost_price: {unit.cost_price}")
                    print(f"      - profit_margin: {unit.profit_margin}")
                    print(f"      - discount_percentage: {unit.discount_percentage}")
                    print(f"      - is_discount_active: {unit.is_discount_active}")
        except Exception as e:
            print(f"❌ Error querying products: {e}")
            import traceback
            traceback.print_exc()
        
    finally:
        db.close()

if __name__ == "__main__":
    check_database()
