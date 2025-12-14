"""
ProductBridge.py - Python-QML Bridge for Product Management
Exposes product CRUD operations to QML layer
"""
from PySide6.QtCore import QObject, Signal, Slot, Property
from sqlalchemy import text
from database.db import SessionLocal
from controllers.product_controller import ProductController


class ProductBridge(QObject):
    """Bridge between QML and Python Product logic"""
    
    # Signals to QML
    productsUpdated = Signal()
    productError = Signal(str)
    productSuccess = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.db = SessionLocal()
        self.product_controller = ProductController(self.db)
        self._products = []
        self._total_count = 0
        self._current_page = 1
        self._page_size = 50
    
    @Property(list, notify=productsUpdated)
    def products(self):
        """Get current product list"""
        return self._products
    
    @Property(int, notify=productsUpdated)
    def totalCount(self):
        """Get total product count"""
        return self._total_count
    
    @Property(int, notify=productsUpdated)
    def currentPage(self):
        """Get current page number"""
        return self._current_page
    
    @Property(int, notify=productsUpdated)
    def totalPages(self):
        """Get total number of pages"""
        import math
        return math.ceil(self._total_count / self._page_size) if self._total_count > 0 else 1
    
    @Slot(int, str)
    def loadProducts(self, page: int = 1, search_query: str = ""):
        """
        Load products with pagination and search
        
        Args:
            page: Page number (1-indexed)
            search_query: Search text
        """
        try:
            self._current_page = page
            products, total = self.product_controller.get_products_paginated(
                page=page,
                page_size=self._page_size,
                search_query=search_query if search_query else None
            )
            
            self._total_count = total
            self._products = []
            
            for p in products:
                # Calculate margin
                margin = 0.0
                if p.price > 0:
                    margin = ((p.price - p.cost_price) / p.price) * 100
                
                self._products.append({
                    "id": p.id,
                    "name": p.name,
                    "sku": p.sku or "",
                    "location": p.location or "",
                    "cost_price": float(p.cost_price),
                    "price": float(p.price),
                    "margin": margin,
                    "stock": float(p.stock),
                    "min_stock": float(p.min_stock) if hasattr(p, 'min_stock') else 5.0,
                    "is_box": p.is_box,
                    "conversion_factor": p.conversion_factor,
                    "unit_type": p.unit_type,
                    "low_stock": p.stock <= (p.min_stock if hasattr(p, 'min_stock') else 5.0)
                })
            
            self.productsUpdated.emit()
        except Exception as e:
            print(f"Error loading products: {e}")
            self.productError.emit(f"Error al cargar productos: {str(e)}")
    
    @Slot(str, str, float, float, float, float, bool, int, str, str)
    def createProduct(self, name: str, sku: str, price: float, cost_price: float, 
                     stock: float, min_stock: float, is_box: bool, 
                     conversion_factor: int, unit_type: str, location: str):
        """
        Create a new product
        
        Args:
            name: Product name
            sku: Product SKU/code
            price: Sale price
            cost_price: Cost price
            stock: Initial stock
            min_stock: Minimum stock alert level
            is_box: Whether product is sold by box
            conversion_factor: Units per box
            unit_type: Unit type (Unidad, Metro, Kilo, Litro)
            location: Storage location
        """
        try:
            self.product_controller.create_product(
                name=name,
                sku=sku if sku else None,
                price=price,
                cost_price=cost_price,
                stock=stock,
                min_stock=min_stock,
                is_box=is_box,
                conversion_factor=conversion_factor,
                unit_type=unit_type,
                location=location if location else None
            )
            self.productSuccess.emit("Producto creado exitosamente")
            self.loadProducts(self._current_page)
        except Exception as e:
            print(f"Error creating product: {e}")
            self.productError.emit(f"Error al crear producto: {str(e)}")
    
    @Slot(int, str, str, float, float, float, float, bool, int, str, str)
    def updateProduct(self, product_id: int, name: str, sku: str, price: float, 
                     cost_price: float, stock: float, min_stock: float, is_box: bool,
                     conversion_factor: int, unit_type: str, location: str):
        """
        Update an existing product
        
        Args:
            product_id: Product ID
            name: Product name
            sku: Product SKU/code
            price: Sale price
            cost_price: Cost price
            stock: Current stock
            min_stock: Minimum stock alert level
            is_box: Whether product is sold by box
            conversion_factor: Units per box
            unit_type: Unit type
            location: Storage location
        """
        try:
            self.product_controller.update_product(
                product_id=product_id,
                name=name,
                sku=sku if sku else None,
                price=price,
                cost_price=cost_price,
                stock=stock,
                min_stock=min_stock,
                is_box=is_box,
                conversion_factor=conversion_factor,
                unit_type=unit_type,
                location=location if location else None
            )
            self.productSuccess.emit("Producto actualizado exitosamente")
            self.loadProducts(self._current_page)
        except Exception as e:
            print(f"Error updating product: {e}")
            self.productError.emit(f"Error al actualizar producto: {str(e)}")
    
    @Slot(int)
    def deleteProduct(self, product_id: int):
        """
        Delete (deactivate) a product
        
        Args:
            product_id: Product ID
        """
        try:
            self.product_controller.delete_product(product_id)
            self.productSuccess.emit("Producto eliminado exitosamente")
            self.loadProducts(self._current_page)
        except Exception as e:
            print(f"Error deleting product: {e}")
            self.productError.emit(f"Error al eliminar producto: {str(e)}")
    
    @Slot(int, result="QVariantMap")
    def getProduct(self, product_id: int):
        """
        Get a single product by ID
        
        Args:
            product_id: Product ID
            
        Returns:
            Product data dict
        """
        try:
            p = self.product_controller.get_product_by_id(product_id)
            if not p:
                return {}
            
            return {
                "id": p.id,
                "name": p.name,
                "sku": p.sku or "",
                "location": p.location or "",
                "cost_price": float(p.cost_price),
                "price": float(p.price),
                "stock": float(p.stock),
                "min_stock": float(p.min_stock) if hasattr(p, 'min_stock') else 5.0,
                "is_box": p.is_box,
                "conversion_factor": p.conversion_factor,
                "unit_type": p.unit_type
            }
        except Exception as e:
            print(f"Error getting product: {e}")
            return {}
    
    def __del__(self):
        """Cleanup database connection"""
        if hasattr(self, 'db'):
            self.db.close()
