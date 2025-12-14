from frontend_caja.services.purchase_service import PurchaseService
import datetime

class PurchaseController:
    def __init__(self, db=None):
        self.service = PurchaseService()
        self.db = None  # Ignored

    def create_purchase_order(self, supplier_id, items, expected_delivery=None, notes=None):
        """
        Create a new purchase order
        items: list of dicts with {product_id, quantity, unit_cost}
        """
        order_data = {
            "supplier_id": supplier_id,
            "items": items,
            "expected_delivery": expected_delivery.isoformat() if expected_delivery else None,
            "notes": notes
        }
        
        result = self.service.create_purchase_order(order_data)
        if result:
            return PurchaseOrderObj(result), None
        else:
            return None, "Error creating purchase order"

    def get_all_purchase_orders(self, status=None):
        """Get all purchase orders, optionally filtered by status"""
        data = self.service.get_all_purchase_orders(status)
        return [PurchaseOrderObj(order) for order in data] if data else []

    def get_purchase_order(self, order_id):
        """Get purchase order by ID"""
        data = self.service.get_purchase_order(order_id)
        return PurchaseOrderObj(data) if data else None

    def receive_purchase_order(self, order_id, user_id=1):
        """
        Receive a purchase order:
        - Update product stock
        - Update product cost_price
        - Create Kardex entries
        - Mark order as RECEIVED
        """
        result = self.service.receive_purchase_order(order_id, user_id)
        if result:
            return True, "Orden recibida correctamente. Stock e inventario actualizados."
        else:
            return False, "Error receiving purchase order"

    def cancel_purchase_order(self, order_id):
        """Cancel a purchase order"""
        result = self.service.cancel_purchase_order(order_id)
        if result:
            return True, "Orden cancelada"
        else:
            return False, "Error cancelling purchase order"

class PurchaseOrderObj:
    """Helper to wrap purchase order dict for UI compatibility"""
    def __init__(self, data):
        self.id = data.get('id')
        self.supplier_id = data.get('supplier_id')
        self.order_date = data.get('order_date')
        if isinstance(self.order_date, str):
            try:
                self.order_date = datetime.datetime.fromisoformat(self.order_date)
            except:
                self.order_date = datetime.datetime.now()
        self.total_amount = data.get('total_amount')
        self.status = data.get('status')
        self.expected_delivery = data.get('expected_delivery')
        self.received_date = data.get('received_date')
        self.received_by = data.get('received_by')
        self.notes = data.get('notes')
        
        # Wrap supplier and details
        supplier_data = data.get('supplier')
        self.supplier = SupplierObj(supplier_data) if supplier_data else None
        
        details_data = data.get('details', [])
        self.details = [PurchaseDetailObj(d) for d in details_data]

class PurchaseDetailObj:
    """Helper to wrap purchase detail dict"""
    def __init__(self, data):
        self.id = data.get('id')
        self.product_id = data.get('product_id')
        self.quantity = data.get('quantity')
        self.unit_cost = data.get('unit_cost')
        self.subtotal = data.get('subtotal')
        product_data = data.get('product')
        self.product = ProductObj(product_data) if product_data else None

class SupplierObj:
    """Helper to wrap supplier dict"""
    def __init__(self, data):
        self.id = data.get('id')
        self.name = data.get('name', 'Proveedor')
        self.contact_name = data.get('contact_name')
        self.phone = data.get('phone')
        self.email = data.get('email')

class ProductObj:
    """Helper to wrap product dict"""
    def __init__(self, data):
        self.id = data.get('id')
        self.name = data.get('name', 'Producto')
        self.sku = data.get('sku')
        self.price = data.get('price')
        self.stock = data.get('stock')
