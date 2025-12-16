"""
Inventory Service - Business logic for stock management with unit conversion
"""

from sqlalchemy.orm import Session
from ..models.models import Product, ProductUnit


class InventoryService:
    """Service layer for inventory operations with automatic unit conversion"""
    
    @staticmethod
    def deduct_stock(db: Session, product_id: int, unit_id: int = None, quantity: float = 1.0):
        """
        Deduct stock from product inventory with automatic unit conversion.
        
        Args:
            db: Database session
            product_id: ID of the product
            unit_id: ID of the ProductUnit (presentation), None for base unit
            quantity: Quantity sold in the specified unit
            
        Returns:
            dict: {
                "success": bool,
                "stock_deducted": float,  # Amount deducted in base units
                "remaining_stock": float,
                "unit_name": str,
                "product_name": str
            }
            
        Raises:
            ValueError: If product not found, insufficient stock, or invalid unit
            
        Example:
            # Sell 2 "Sacos de 20kg" (unit_id=5, factor=20.0)
            # This will deduct 40.0 from product.stock
            result = InventoryService.deduct_stock(db, product_id=1, unit_id=5, quantity=2.0)
            # result["stock_deducted"] == 40.0
        """
        # Get product
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError(f"Product with ID {product_id} not found")
        
        # Calculate base units to deduct
        if unit_id is None:
            # Selling in base units
            base_units_to_deduct = quantity
            unit_name = product.base_unit.value
        else:
            # Selling in a specific presentation
            unit = db.query(ProductUnit).filter(ProductUnit.id == unit_id).first()
            if not unit:
                raise ValueError(f"ProductUnit with ID {unit_id} not found")
            
            if unit.product_id != product_id:
                raise ValueError(
                    f"ProductUnit {unit_id} does not belong to Product {product_id}"
                )
            
            if not unit.is_active:
                raise ValueError(f"ProductUnit '{unit.name}' is not active")
            
            # Convert to base units
            base_units_to_deduct = quantity * unit.conversion_factor
            unit_name = unit.name
        
        # Check stock availability
        if product.stock < base_units_to_deduct:
            raise ValueError(
                f"Insufficient stock for '{product.name}'. "
                f"Available: {product.stock} {product.base_unit.value}, "
                f"Required: {base_units_to_deduct} {product.base_unit.value}"
            )
        
        # Deduct stock
        product.stock -= base_units_to_deduct
        db.commit()
        
        return {
            "success": True,
            "stock_deducted": base_units_to_deduct,
            "remaining_stock": product.stock,
            "unit_name": unit_name,
            "product_name": product.name
        }
    
    @staticmethod
    def get_unit_by_barcode(db: Session, barcode: str):
        """
        Find a ProductUnit by barcode, or fallback to Product.sku
        
        Args:
            db: Database session
            barcode: Barcode to search for
            
        Returns:
            tuple: (product, product_unit or None)
            
        Example:
            # Scan barcode "7891234567890"
            product, unit = InventoryService.get_unit_by_barcode(db, "7891234567890")
            if unit:
                print(f"Found presentation: {unit.name}")
            else:
                print(f"Found base product: {product.name}")
        """
        # First, check ProductUnit table (presentations have priority)
        unit = db.query(ProductUnit).filter(
            ProductUnit.barcode == barcode,
            ProductUnit.is_active == True
        ).first()
        
        if unit:
            return (unit.product, unit)
        
        # Fallback to Product.sku (base unit)
        product = db.query(Product).filter(Product.sku == barcode).first()
        if product:
            return (product, None)
        
        return (None, None)
    
    @staticmethod
    def add_stock(db: Session, product_id: int, unit_id: int = None, quantity: float = 1.0):
        """
        Add stock to product inventory with automatic unit conversion.
        
        Args:
            db: Database session
            product_id: ID of the product
            unit_id: ID of the ProductUnit (presentation), None for base unit
            quantity: Quantity to add in the specified unit
            
        Returns:
            dict: Similar to deduct_stock but with stock_added instead
        """
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError(f"Product with ID {product_id} not found")
        
        # Calculate base units to add
        if unit_id is None:
            base_units_to_add = quantity
            unit_name = product.base_unit.value
        else:
            unit = db.query(ProductUnit).filter(ProductUnit.id == unit_id).first()
            if not unit:
                raise ValueError(f"ProductUnit with ID {unit_id} not found")
            
            if unit.product_id != product_id:
                raise ValueError(
                    f"ProductUnit {unit_id} does not belong to Product {product_id}"
                )
            
            base_units_to_add = quantity * unit.conversion_factor
            unit_name = unit.name
        
        # Add stock
        product.stock += base_units_to_add
        db.commit()
        
        return {
            "success": True,
            "stock_added": base_units_to_add,
            "new_stock": product.stock,
            "unit_name": unit_name,
            "product_name": product.name
        }
    
    @staticmethod
    def get_product_presentations(db: Session, product_id: int):
        """
        Get all active presentations for a product
        
        Args:
            db: Database session
            product_id: ID of the product
            
        Returns:
            list: List of ProductUnit objects
        """
        return db.query(ProductUnit).filter(
            ProductUnit.product_id == product_id,
            ProductUnit.is_active == True
        ).all()
