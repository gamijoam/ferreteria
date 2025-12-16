"""
Example usage of the Multi-Unit Product System
Demonstrates how to create products with multiple presentations and use InventoryService
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ferreteria_refactor.backend_api.database.db import SessionLocal
from ferreteria_refactor.backend_api.models.models import Product, ProductUnit, UnitType
from ferreteria_refactor.backend_api.services import InventoryService


def example_create_product_with_units():
    """Example: Create a product with multiple presentations"""
    print("\n" + "="*70)
    print("[EXAMPLE 1] Creating product with multiple presentations")
    print("="*70)
    
    db = SessionLocal()
    try:
        # Create base product (Cement)
        cement = Product(
            name="Cemento Gris",
            sku="7891234567890",  # Base unit barcode
            description="Cemento gris para construcción",
            price=5.50,  # Price per KG
            cost_price=4.00,
            stock=1000.0,  # 1000 KG in stock
            base_unit=UnitType.KG,  # Base unit is kilograms
            is_active=True
        )
        
        db.add(cement)
        db.flush()  # Get the ID
        
        # Create presentations
        
        # 1. Saco de 50kg
        saco_50kg = ProductUnit(
            product_id=cement.id,
            name="Saco 50kg",
            conversion_factor=50.0,  # 1 saco = 50 kg
            barcode="7891234567891",  # Unique barcode for this presentation
            price=250.00,  # Optional: override price (otherwise 5.50 * 50 = 275)
            is_default_sale=True,  # Default in POS
            is_active=True
        )
        
        # 2. Saco de 25kg
        saco_25kg = ProductUnit(
            product_id=cement.id,
            name="Saco 25kg",
            conversion_factor=25.0,  # 1 saco = 25 kg
            barcode="7891234567892",
            price=None,  # Will calculate: 5.50 * 25 = 137.50
            is_default_sale=False,
            is_active=True
        )
        
        # 3. Pallet (40 sacos de 50kg)
        pallet = ProductUnit(
            product_id=cement.id,
            name="Pallet (40 sacos)",
            conversion_factor=2000.0,  # 1 pallet = 2000 kg (40 * 50)
            barcode="7891234567893",
            price=9500.00,  # Bulk discount
            is_default_sale=False,
            is_active=True
        )
        
        db.add_all([saco_50kg, saco_25kg, pallet])
        db.commit()
        
        print(f"[OK] Created product: {cement.name}")
        print(f"[OK] Base unit: {cement.base_unit.value}")
        print(f"[OK] Stock: {cement.stock} {cement.base_unit.value}")
        print(f"[OK] Created {len(cement.units)} presentations:")
        for unit in cement.units:
            price_info = f"${unit.price}" if unit.price else f"${cement.price * unit.conversion_factor} (calculated)"
            print(f"  - {unit.name}: {unit.conversion_factor} {cement.base_unit.value}, {price_info}")
        
        return cement.id
        
    except Exception as e:
        print(f"[ERROR] {e}")
        db.rollback()
        raise
    finally:
        db.close()


def example_barcode_scanning(product_id):
    """Example: Scan different barcodes and get the right presentation"""
    print("\n" + "="*70)
    print("[EXAMPLE 2] Barcode scanning")
    print("="*70)
    
    db = SessionLocal()
    try:
        # Scan base product barcode
        product, unit = InventoryService.get_unit_by_barcode(db, "7891234567890")
        if product:
            print(f"\n[SCAN] Barcode: 7891234567890")
            print(f"[OK] Product: {product.name}")
            print(f"[OK] Unit: {'Base unit (' + product.base_unit.value + ')' if not unit else unit.name}")
        
        # Scan Saco 50kg barcode
        product, unit = InventoryService.get_unit_by_barcode(db, "7891234567891")
        if product and unit:
            print(f"\n[SCAN] Barcode: 7891234567891")
            print(f"[OK] Product: {product.name}")
            print(f"[OK] Unit: {unit.name} (factor: {unit.conversion_factor})")
        
        # Scan Pallet barcode
        product, unit = InventoryService.get_unit_by_barcode(db, "7891234567893")
        if product and unit:
            print(f"\n[SCAN] Barcode: 7891234567893")
            print(f"[OK] Product: {product.name}")
            print(f"[OK] Unit: {unit.name} (factor: {unit.conversion_factor})")
        
    finally:
        db.close()


def example_stock_operations(product_id):
    """Example: Deduct and add stock with automatic conversion"""
    print("\n" + "="*70)
    print("[EXAMPLE 3] Stock operations with unit conversion")
    print("="*70)
    
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        print(f"\n[INFO] Product: {product.name}")
        print(f"[INFO] Initial stock: {product.stock} {product.base_unit.value}")
        
        # Get the Saco 50kg unit
        saco_50kg = db.query(ProductUnit).filter(
            ProductUnit.product_id == product_id,
            ProductUnit.name == "Saco 50kg"
        ).first()
        
        # Sell 3 sacos of 50kg
        print(f"\n[OPERATION] Selling 3 x {saco_50kg.name}")
        result = InventoryService.deduct_stock(
            db=db,
            product_id=product_id,
            unit_id=saco_50kg.id,
            quantity=3.0
        )
        
        print(f"[OK] Stock deducted: {result['stock_deducted']} {product.base_unit.value}")
        print(f"[OK] Remaining stock: {result['remaining_stock']} {product.base_unit.value}")
        
        # Add stock: Receive 1 pallet
        pallet = db.query(ProductUnit).filter(
            ProductUnit.product_id == product_id,
            ProductUnit.name.like("Pallet%")
        ).first()
        
        print(f"\n[OPERATION] Receiving 1 x {pallet.name}")
        result = InventoryService.add_stock(
            db=db,
            product_id=product_id,
            unit_id=pallet.id,
            quantity=1.0
        )
        
        print(f"[OK] Stock added: {result['stock_added']} {product.base_unit.value}")
        print(f"[OK] New stock: {result['new_stock']} {product.base_unit.value}")
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def main():
    print("\n" + "="*70)
    print("[START] MULTI-UNIT PRODUCT SYSTEM - USAGE EXAMPLES")
    print("="*70)
    
    # Example 1: Create product with units
    product_id = example_create_product_with_units()
    
    # Example 2: Barcode scanning
    example_barcode_scanning(product_id)
    
    # Example 3: Stock operations
    example_stock_operations(product_id)
    
    print("\n" + "="*70)
    print("[COMPLETE] All examples completed successfully!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
