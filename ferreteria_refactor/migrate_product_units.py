"""
Migration script to convert existing products to multi-unit system.
Migrates is_box products to ProductUnit records and sets base_unit for all products.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import text
from ferreteria_refactor.backend_api.database.db import SessionLocal
from ferreteria_refactor.backend_api.models.models import Product, ProductUnit, UnitType


def migrate_product_units():
    """
    Migrate existing products from is_box/conversion_factor to ProductUnit system
    """
    print("\n" + "="*70)
    print("[MIGRATION] CONVERTING PRODUCTS TO MULTI-UNIT SYSTEM")
    print("="*70)
    
    db = SessionLocal()
    
    try:
        # Step 1: Add base_unit column if not exists
        print("\n[STEP 1] Adding base_unit column to products table...")
        try:
            db.execute(text("""
                ALTER TABLE products 
                ADD COLUMN IF NOT EXISTS base_unit VARCHAR DEFAULT 'UNIDAD';
            """))
            db.commit()
            print("[OK] base_unit column added")
        except Exception as e:
            print(f"[INFO] base_unit column may already exist: {e}")
            db.rollback()
        
        # Step 2: Get all products with is_box = True
        print("\n[STEP 2] Finding products with is_box=True...")
        products_with_box = db.query(Product).filter(Product.is_box == True).all()
        print(f"[INFO] Found {len(products_with_box)} products with is_box=True")
        
        migrated_count = 0
        skipped_count = 0
        
        for product in products_with_box:
            # Check if ProductUnit already exists for this product
            existing_unit = db.query(ProductUnit).filter(
                ProductUnit.product_id == product.id,
                ProductUnit.name == "Caja"
            ).first()
            
            if existing_unit:
                print(f"[SKIP] Product '{product.name}' already has a 'Caja' unit")
                skipped_count += 1
                continue
            
            # Create ProductUnit for the box presentation
            unit = ProductUnit(
                product_id=product.id,
                name="Caja",
                conversion_factor=float(product.conversion_factor),
                barcode=product.sku if product.sku else None,  # Inherit barcode
                is_default_sale=True,  # Set as default for POS
                is_active=True
            )
            
            db.add(unit)
            migrated_count += 1
            print(f"[OK] Migrated '{product.name}': Caja x{product.conversion_factor}")
        
        db.commit()
        print(f"\n[STEP 3] Migration summary:")
        print(f"  - Migrated: {migrated_count} products")
        print(f"  - Skipped: {skipped_count} products (already migrated)")
        
        # Step 3: Set default base_unit for all products
        print("\n[STEP 4] Setting default base_unit for all products...")
        all_products = db.query(Product).all()
        updated_count = 0
        
        for product in all_products:
            # Only update if base_unit is not set or is the default string
            if not hasattr(product, 'base_unit') or product.base_unit is None:
                product.base_unit = UnitType.UNIDAD
                updated_count += 1
        
        db.commit()
        print(f"[OK] Set base_unit=UNIDAD for {updated_count} products")
        
        # Step 4: Summary statistics
        print("\n[STEP 5] Final statistics...")
        total_products = db.query(Product).count()
        total_units = db.query(ProductUnit).count()
        
        print(f"  - Total products: {total_products}")
        print(f"  - Total product units: {total_units}")
        print(f"  - Products with presentations: {db.query(Product).join(ProductUnit).distinct().count()}")
        
        print("\n" + "="*70)
        print("[SUCCESS] Migration completed successfully!")
        print("="*70)
        print("\n[NEXT STEPS]")
        print("1. Run verify_product_units.py to validate the migration")
        print("2. Update POS/sales logic to use ProductUnit for barcode scanning")
        print("3. After validation, consider removing is_box and conversion_factor columns")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate_product_units()
