from frontend_caja.services.return_service import ReturnService
import datetime

class ReturnController:
    def __init__(self, db=None):
        self.service = ReturnService()
        self.db = None  # Ignored

    def find_sale(self, sale_id: int):
        """Find sale by ID"""
        data = self.service.get_sale_for_return(sale_id)
        return SaleObj(data) if data else None

    def get_recent_sales(self, limit=50):
        """Get recent sales"""
        data = self.service.search_sales()
        return [SaleObj(s) for s in data] if data else []

    def search_sales(self, query: str):
        """Search sales by ID or customer name"""
        data = self.service.search_sales(query)
        return [SaleObj(s) for s in data] if data else []

    def process_return(self, sale_id: int, items_to_return: list, reason: str, refund_currency: str = "USD", exchange_rate: float = 1.0):
        """
        Process a return
        items_to_return: List of dicts {product_id, quantity}
        """
        payload = {
            "sale_id": sale_id,
            "items": items_to_return,
            "reason": reason,
            "refund_currency": refund_currency,
            "exchange_rate": exchange_rate
        }
        
        result = self.service.process_return(payload)
        if result:
            return ReturnObj(result)
        else:
            raise Exception("Error procesando devolución")

    def get_returns(self, skip=0, limit=100):
        """Get list of returns"""
        data = self.service.get_returns(skip, limit)
        return [ReturnObj(r) for r in data]

    def get_return(self, return_id):
        """Get specific return"""
        data = self.service.get_return(return_id)
        return ReturnObj(data) if data else None

class SaleObj:
    """Helper to wrap sale dict for UI compatibility"""
    def __init__(self, data):
        self.id = data.get('id')
        self.date = data.get('date')
        if isinstance(self.date, str):
            try:
                self.date = datetime.datetime.fromisoformat(self.date)
            except:
                self.date = datetime.datetime.now()
        self.total_amount = data.get('total_amount')
        self.payment_method = data.get('payment_method')
        self.customer_id = data.get('customer_id')
        customer_data = data.get('customer')
        self.customer = CustomerObj(customer_data) if customer_data else None
        # Wrap details
        details_data = data.get('details', [])
        self.details = [SaleDetailObj(d) for d in details_data]

class SaleDetailObj:
    """Helper to wrap sale detail dict"""
    def __init__(self, data):
        self.id = data.get('id')
        self.product_id = data.get('product_id')
        self.quantity = data.get('quantity')
        self.unit_price = data.get('unit_price')
        self.subtotal = data.get('subtotal')
        self.is_box_sale = data.get('is_box_sale', False)
        product_data = data.get('product')
        self.product = ProductObj(product_data) if product_data else None

class ProductObj:
    """Helper to wrap product dict"""
    def __init__(self, data):
        self.id = data.get('id')
        self.name = data.get('name', 'Producto')
        self.sku = data.get('sku')
        self.price = data.get('price')
        self.stock = data.get('stock')

class CustomerObj:
    """Helper to wrap customer dict"""
    def __init__(self, data):
        self.id = data.get('id')
        self.name = data.get('name', 'Sin nombre')
        self.phone = data.get('phone')
        self.email = data.get('email')

class ReturnObj:
    """Helper to wrap dict response for UI compatibility"""
    def __init__(self, data):
        self.id = data.get('id')
        self.sale_id = data.get('sale_id')
        self.date = data.get('date')
        if isinstance(self.date, str):
            try:
                self.date = datetime.datetime.fromisoformat(self.date)
            except:
                self.date = datetime.datetime.now()
        self.total_refunded = data.get('total_refunded')
        self.reason = data.get('reason')
        self.details = data.get('details', [])
