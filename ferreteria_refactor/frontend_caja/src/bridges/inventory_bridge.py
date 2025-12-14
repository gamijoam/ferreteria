from PySide6.QtCore import QObject, Signal, Slot, Property
from src.controllers.inventory_controller import InventoryController
from src.database.db import SessionLocal
from src.models.models import Product

class InventoryBridge(QObject):
    inventoryUpdated = Signal()
    historyLoaded = Signal(list)
    operationError = Signal(str)
    operationSuccess = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.db = SessionLocal()
        self.controller = InventoryController(self.db)
        
    @Slot(int, float, bool)
    def addStock(self, product_id, quantity, is_box):
        try:
            self.controller.add_stock(product_id, quantity, is_box)
            self.inventoryUpdated.emit()
            self.operationSuccess.emit("Entrada registrada correctamente")
        except Exception as e:
            self.operationError.emit(str(e))
            
    @Slot(int, float, str)
    def removeStock(self, product_id, quantity, reason):
        try:
            self.controller.remove_stock(product_id, quantity, reason)
            self.inventoryUpdated.emit()
            self.operationSuccess.emit("Salida registrada correctamente")
        except Exception as e:
            self.operationError.emit(str(e))
            
    @Slot(int)
    def getKardex(self, product_id):
        try:
            # If product_id is 0, get all (controller supports it?)
            # Controller.get_kardex(product_id) filters by product_id if provided.
            # If product_id is None, it returns all? Let's check controller.
            # Looking at previous view, it passed product_id.
            
            # Handling 0 as None for "All"
            pid = product_id if product_id > 0 else None
            
            movements = self.controller.get_kardex(pid)
            
            result = []
            for mov in movements:
                result.append({
                    "date": mov.date.strftime("%Y-%m-%d %H:%M"),
                    "product_name": mov.product.name if mov.product else "Desconocido",
                    "type": mov.movement_type.value,
                    "quantity": mov.quantity,
                    "balance": mov.balance_after,
                    "description": mov.description or ""
                })
            
            self.historyLoaded.emit(result)
            return result # Return for synchronous use if needed, but signal is main way
        except Exception as e:
            self.operationError.emit(str(e))
            return []

    @Slot(str, result=list)
    def searchProducts(self, query):
        """Search products for autocomplete"""
        if not query or len(query) < 2:
            return []
            
        products = self.db.query(Product).filter(
            (Product.name.ilike(f"%{query}%")) | (Product.sku.ilike(f"%{query}%")),
            Product.is_active == True
        ).limit(20).all()
        
        return [
            {
                "id": p.id,
                "name": p.name,
                "sku": p.sku,
                "stock": p.stock,
                "unit_type": p.unit_type,
                "is_box": p.is_box,
                "conversion_factor": p.conversion_factor
            }
            for p in products
        ]
