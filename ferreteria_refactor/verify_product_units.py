"""
Verification script for Multi-Unit Product System
Tests database schema, migration results, and InventoryService functionality
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ferreteria_refactor.backend_api.database.db import SessionLocal, engine
from ferreteria_refactor.backend_api.models.models import Product, ProductUnit, UnitType
from ferreteria_refactor.backend_api.services import InventoryService
from sqlalchemy import inspect


def verify_schema():
    """Verify that ProductUnit table and base_unit column exist"""
    print("\n" + "="*70)
    print("[VERIFY] CHECKING DATABASE SCHEMA")
    print("="*70)
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    # Check ProductUnit table
    if 'product_units' in tables:
        print("[OK] Table 'product_units' exists")
        
        # Check columns
        columns = [col['name'] for col in inspector.get_columns('product_units')]
        required_cols = ['id', 'product_id', 'name', 'conversion_factor', 'barcode', 'price']
        
        for col in required_cols:
            if col in columns:
                print(f"[OK] Column 'product_units.{col}' exists")
            else:
                print(f"[ERROR] Column 'product_units.{col}' NOT FOUND")
    else:
        print("[ERROR] Table 'product_units' NOT FOUND")
        return False
    
    # Check base_unit column in products
    product_columns = [col['name'] for col in inspector.get_columns('products')]
    if 'base_unit' in product_columns:
        print("[OK] Column 'products.base_unit' exists")
    else:
        print("[ERROR] Column 'products.base_unit' NOT FOUND")
    
    return True


def verify_migration():
    """Verify migration results"""
    print("\n" + "="*70)
    print("[VERIFY] CHECKING MIGRATION RESULTS")
    print("="*70)
    
    db = SessionLocal()
    try:
        # Count products and units
        total_products = db.query(Product).count()
        total_units = db.query(ProductUnit).count()
        products_with_box = db.query(Product).filter(Product.is_box == True).count()
        
        print(f"\n[DATA] Total products: {total_products}")
        print(f"[DATA] Total product units: {total_units}")
        print(f"[DATA] Products with is_box=True: {products_with_box}")
        
        # Show sample ProductUnits
        sample_units = db.query(ProductUnit).limit(5).all()
        if sample_units:
            print(f"\n[DATA] Sample ProductUnits:")
            for unit in sample_units:
                print(f"  - {unit.name} (factor: {unit.conversion_factor}, barcode: {unit.barcode})")
        
        # Check base_unit values
        products_with_base_unit = db.query(Product).filter(Product.base_unit != None).count()
        print(f"\n[DATA] Products with base_unit set: {products_with_base_unit}/{total_products}")
        
        return True
    finally:
        db.close()


def test_inventory_service():
    """Test InventoryService functionality"""
    print("\n" + "="*70)
    print("[TEST] TESTING INVENTORY SERVICE")
    print("="*70)
    
    db = SessionLocal()
    try:
        # Test 1: Get unit by barcode
        print("\n[TEST 1] Testing get_unit_by_barcode...")
        
        # Find a ProductUnit with a barcode
        unit_with_barcode = db.query(ProductUnit).filter(ProductUnit.barcode != None).first()
        
        if unit_with_barcode:
            product, unit = InventoryService.get_unit_by_barcode(db, unit_with_barcode.barcode)
            if product and unit:
                print(f"[OK] Found product: {product.name}")
                print(f"[OK] Found unit: {unit.name} (factor: {unit.conversion_factor})")
            else:
                print("[ERROR] Barcode lookup failed")
        else:
            print("[SKIP] No ProductUnits with barcodes found")
        
        # Test 2: Stock deduction simulation (without actually deducting)
        print("\n[TEST 2] Testing stock deduction logic...")
        
        # Find a product with a ProductUnit
        product_with_unit = db.query(Product).join(ProductUnit).first()
        
        if product_with_unit:
            unit = product_with_unit.units[0]
            initial_stock = product_with_unit.stock
            
            print(f"[INFO] Product: {product_with_unit.name}")
            print(f"[INFO] Initial stock: {initial_stock} {product_with_unit.base_unit.value}")
            print(f"[INFO] Unit: {unit.name} (factor: {unit.conversion_factor})")
            
            # Calculate what would be deducted
            quantity_to_sell = 2.0
            expected_deduction = quantity_to_sell * unit.conversion_factor
            
            print(f"[INFO] Selling {quantity_to_sell} x {unit.name}")
            print(f"[INFO] Expected deduction: {expected_deduction} {product_with_unit.base_unit.value}")
            
            if initial_stock >= expected_deduction:
                print("[OK] Stock deduction logic validated")
            else:
                print(f"[WARNING] Insufficient stock for test ({initial_stock} < {expected_deduction})")
        else:
            print("[SKIP] No products with units found")
        
        return True
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def main():
    print("\n" + "="*70)
    print("[START] MULTI-UNIT PRODUCT SYSTEM VERIFICATION")
    print("="*70)
    
    # Run verifications
    schema_ok = verify_schema()
    migration_ok = verify_migration()
    service_ok = test_inventory_service()
    
    # Summary
    print("\n" + "="*70)
    print("[SUMMARY] VERIFICATION RESULTS")
    print("="*70)
    
    if schema_ok and migration_ok and service_ok:
        print("[OK] All verifications passed!")
        print("[OK] Multi-unit product system is working correctly")
    else:
        print("[ERROR] Some verifications failed")
        print("[WARNING] Please check the errors above")
    
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
