from frontend_caja.services.quote_service import QuoteService
import datetime

class QuoteObj:
    """Helper to wrap dict response as object for UI compatibility"""
    def __init__(self, data):
        self.id = data.get('id')
        # Parse date if string
        raw_date = data.get('date')
        if isinstance(raw_date, str):
            try:
                self.date = datetime.datetime.fromisoformat(raw_date)
            except ValueError:
                self.date = datetime.datetime.now() # Fallback
        else:
            self.date = raw_date
            
        self.customer_id = data.get('customer_id')
        self.total_amount = data.get('total_amount')
        self.status = data.get('status', 'PENDING')
        self.notes = data.get('notes')
        self.details = [] 
        if 'details' in data:
            self.details = [QuoteDetailObj(d) for d in data['details']]
        self.customer = None
        if 'customer' in data and data['customer']:
            self.customer = CustomerObj(data['customer'])

class CustomerObj:
    def __init__(self, data):
        self.name = data.get('name', 'N/A')

class QuoteDetailObj:
    def __init__(self, data):
        self.product_id = data.get('product_id')
        self.quantity = data.get('quantity')
        self.unit_price = data.get('unit_price')
        self.subtotal = data.get('subtotal')
        self.is_box_sale = data.get('is_box_sale')
        self.product = ProductObj(data.get('product')) if data.get('product') else None

class ProductObj:
    def __init__(self, data):
        self.id = data.get('id')
        self.name = data.get('name')
        self.sku = data.get('sku')
        self.price = data.get('price')
        self.location = data.get('location')

class QuoteController:
    def __init__(self, db=None):
        self.service = QuoteService()
        self.db = None # Not used

    def save_quote(self, cart: list, customer_id=None, notes=""):
        """Save current cart as a quote via API"""
        if not cart:
            raise ValueError("El carrito está vacío")
        
        # Prepare payload for API
        items_payload = []
        for item in cart:
            items_payload.append({
                "product_id": item["product_id"],
                "quantity": item["quantity"],
                "is_box": item["is_box"],
                "unit_price": item["unit_price"],
                "subtotal": item["subtotal"]
            })

        payload = {
            "customer_id": customer_id,
            "total_amount": sum(item["subtotal"] for item in cart),
            "notes": notes,
            "items": items_payload
        }
        
        result = self.service.create_quote(payload)
        if result:
            return QuoteObj(result)
        else:
            raise Exception("Error saving quote to backend")

    def get_all_quotes(self, status=None):
        """Get all quotes from API"""
        data = self.service.get_all_quotes()
        return [QuoteObj(d) for d in data]

    def convert_to_cart(self, quote_id: int):
        """Convert quote to cart format for POS"""
        # Need to fetch details from API
        quote_data = self.service.get_quote_details(quote_id)
        if not quote_data:
            raise ValueError("Cotización no encontrada o error de conexión")
        
        quote = QuoteObj(quote_data)
        
        cart = []
        for detail in quote.details:
            # Reconstruct cart item
            item = {
                "product_id": detail.product_id,
                "name": detail.product.name if detail.product else "Desconocido",
                "sku": detail.product.sku if detail.product else "",
                "quantity": detail.quantity,
                "units_deducted": detail.quantity, 
                "unit_price": detail.unit_price,
                "subtotal": detail.subtotal,
                "is_box": detail.is_box_sale,
                "product_obj": detail.product
            }
            cart.append(item)
        
        return cart

    def mark_as_converted(self, quote_id: int):
        """Mark quote as converted to sale"""
        result = self.service.mark_quote_converted(quote_id)
        if not result:
            raise Exception("No se pudo actualizar el estado de la cotización")

    def generate_quote_text(self, quote_input, cart=None, customer_name="N/A"):
        """
        Generate printable quote text.
        quote_input can be a quote ID (int) or a QuoteObj.
        If ID, fetches details from API.
        """
        quote_obj = None
        
        # Handle int/ID input (e.g. from history list)
        if isinstance(quote_input, int):
            data = self.service.get_quote_details(quote_input)
            if not data:
                return "Error: No se pudo obtener la cotización."
            quote_obj = QuoteObj(data)
        else:
            # Handle object input (e.g. from save action)
            quote_obj = quote_input
            
        # Ensure we have details. If object came from list view, it might lack details.
        if not quote_obj.details and isinstance(quote_input, int) == False:
             # Try refreshing details
             data = self.service.get_quote_details(quote_obj.id)
             if data:
                 quote_obj = QuoteObj(data)
        
        # Recalculate customer name if available
        if quote_obj.customer:
            customer_name = quote_obj.customer.name

        lines = [
            "=" * 40,
            "COTIZACIÓN",
            "=" * 40,
            f"Número: {quote_obj.id}",
            f"Fecha: {quote_obj.date}",
            f"Cliente: {customer_name}",
            "-" * 40,
            ""
        ]
        
        # Determine items source: argument cart OR object details
        items = []
        if cart:
            items = cart # List of dicts
        elif quote_obj.details:
            items = quote_obj.details # List of QuoteDetailObj
            
        for item in items:
            # Handle both dict and object (polymorphism would be cleaner but this works quick)
            is_dict = isinstance(item, dict)
            
            name = item.get('name', 'Producto') if is_dict else (item.product.name if item.product else "Producto")
            quantity = item.get('quantity') if is_dict else item.quantity
            is_box = item.get('is_box') if is_dict else item.is_box_sale
            unit_price = item.get('unit_price') if is_dict else item.unit_price
            subtotal = item.get('subtotal') if is_dict else item.subtotal
            
            tipo = "CAJA" if is_box else "UNID"
            lines.append(f"{name}")
            lines.append(f"  {quantity} {tipo} x ${unit_price:,.2f} = ${subtotal:,.2f}")
        
        lines.extend([
            "",
            "-" * 40,
            f"TOTAL: ${quote_obj.total_amount:,.2f}",
            "",
            f"Notas: {quote_obj.notes or 'N/A'}",
            "",
            "Esta cotización es válida por 30 días.",
            "=" * 40
        ])
        
        return "\n".join(lines)
