from frontend_caja.services.inventory_service import InventoryService
# from src.utils.event_bus import event_bus # If we had one

class InventoryController:
    def __init__(self, db=None):
        self.service = InventoryService()
        self.db = None # Ignored

    def add_stock(self, product_id: int, quantity: int, is_box_input: bool, description: str = "Compra"):
        """
        Registra una entrada de mercancía (Compra) convertida a unidades en backend.
        """
        payload = {
            "product_id": product_id,
            "quantity": float(quantity), # Ensure float
            "is_box_input": is_box_input,
            "description": description,
            "movement_type": "PURCHASE"
        }
        
        result = self.service.add_stock(payload)
        if result:
            return True, "Stock actualizado" # Or return result['new_stock']
        else:
             raise Exception("Error actualizando stock en servidor")

    def remove_stock(self, product_id: int, quantity: float, description: str = "Ajuste de Salida"):
        """
        Registra una salida de mercancía (Ajuste / Merma / Donación).
        """
        payload = {
            "product_id": product_id,
            "quantity": quantity,
            "description": description,
            "is_box_input": False, # Removal usually in units
            "movement_type": "ADJUSTMENT_OUT"
        }
        
        result = self.service.remove_stock(payload)
        if result:
            return True, "Stock actualizado"
        else:
             raise Exception("Error actualizando stock en servidor")

    def get_kardex(self, product_id: int):
        data_list = self.service.get_kardex(product_id)
        # Convert to objects if view expects objects with .date, .description
        # Or return dicts if view handles it.
        # Assuming view handles objects (it says kardex.description).
        return [KardexObj(d) for d in data_list]

from datetime import datetime

class KardexObj:
    def __init__(self, data):
        self.id = data.get('id')
        date_val = data.get('date')
        if isinstance(date_val, str):
            try:
                self.date = datetime.fromisoformat(date_val)
            except ValueError:
                self.date = datetime.now() # Fallback
        else:
            self.date = date_val or datetime.now()
            
        self.movement_type = MockEnum(data.get('movement_type')) # Use MockEnum to handle .value access in view
        self.quantity = data.get('quantity')
        self.balance_after = data.get('balance_after')
        self.description = data.get('description')
        
        product_data = data.get('product')
        if product_data:
            self.product = SimpleProductObj(product_data)
        else:
            self.product = MockProductRef(data.get('product_id'))

class MockEnum:
    def __init__(self, val):
        self.value = val

class MockProductRef:
    def __init__(self, pid):
        self.name = f"Producto {pid}"

class SimpleProductObj:
    def __init__(self, data):
        self.name = data.get('name', 'Desconocido')
