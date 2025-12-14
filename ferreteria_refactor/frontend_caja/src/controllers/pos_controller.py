from frontend_caja.services.product_service import ProductService
# Using explicit relative imports if running as package, or absolute.
# Since we are inside src, standard import might depend on PYTHONPATH.
# tailored for avoiding DB imports.

class POSController:
    def __init__(self, db=None): # db argument kept for compatibility with view instantiation
        self.product_service = ProductService()
        self.cart = [] # List of dicts
        self.cached_products = [] 
        self.reload_products()

    def reload_products(self):
        """Fetch products from API and update local cache"""
        print("Fetching products from API...")
        try:
            products = self.product_service.get_all_products()
            if products:
                self.cached_products = products
                print(f"Loaded {len(products)} products.")
            else:
                self.cached_products = []
                print("No products loaded.")
        except Exception as e:
            print(f"Error loading products: {e}")
            self.cached_products = []

    def add_to_cart(self, sku_or_name: str, quantity: float, is_box: bool, product_id: int = None):
        """
        Refactored add_to_cart to use cached product list from API.
        """
        product = None
        
        # 1. Find directly by ID if provided (from search widget)
        if product_id:
            for p in self.cached_products:
                if p['id'] == product_id:
                    product = p
                    break
        
        # 2. Find by SKU or Name
        if not product:
            name_lower = sku_or_name.lower()
            for p in self.cached_products:
                if (p.get('sku') and p['sku'] == sku_or_name) or name_lower in p['name'].lower():
                    product = p
                    break
        
        if not product:
            return False, "Producto no encontrado"

        # Simplified Pricing Logic (No rules, just base price + box factor)
        price_to_use = product['price']
        units_to_deduct = quantity
        
        if is_box:
             units_to_deduct = quantity * product['conversion_factor']
             price_to_use = product['price'] * product['conversion_factor']

        subtotal = price_to_use * quantity
        
        item = {
            "product_id": product['id'],
            "name": product['name'],
            "sku": product.get('sku'),
            "quantity": quantity,
            "units_deducted": units_to_deduct,
            "unit_price": price_to_use,
            "subtotal": subtotal,
            "is_box": is_box,
            "unit_type": product.get("unit_type", "Unidad"),
            "product_obj": product # Keep dict as obj
        }
        
        self.cart.append(item)
        return True, "Agregado al carrito"

    def apply_discount(self, index: int, discount_value: float, discount_type: str):
         # Simplistic mock for UI compatibility
         if 0 <= index < len(self.cart):
             # Just store it, don't do complex math for now
             return True, "Descuento simulado"
         return False, "Item invalido"

    def remove_from_cart(self, index: int):
        if 0 <= index < len(self.cart):
            self.cart.pop(index)

    def get_total(self):
        return sum(item["subtotal"] for item in self.cart)

    def finalize_sale(self, payments=None, customer_id=None, is_credit=False, currency="USD", exchange_rate=1.0, notes=""):
        """
        Construct payload and send to API. Arguments kept for signature compatibility.
        """
        if not self.cart:
            return False, "El carrito está vacío", ""

        total = self.get_total()
        
        # Determine main payment method for the simplified backend
        payment_method_str = "Efectivo"
        if payments and len(payments) > 0:
            payment_method_str = payments[0]["method"]

        # Build payload matching schemas.SaleCreate
        sale_payload = {
            "customer_id": customer_id,
            "payment_method": payment_method_str,
            "total_amount": total,
            "items": []
        }

        for item in self.cart:
            sale_payload["items"].append({
                "product_id": item["product_id"],
                "quantity": item["quantity"], 
                "is_box": item["is_box"]
            })

        # Call Service
        print("Sending sale to API...")
        try:
            result = self.product_service.record_sale(sale_payload)
            
            if result and result.get("status") == "success":
                sale_id = result.get("sale_id")
                ticket = f"Venta #{sale_id} Exitosa!\nTotal: ${total:.2f}\n(Procesado por API)"
                self.cart.clear()
                self.reload_products() 
                return True, "¡Venta Registrada!", ticket
            else:
                return False, "Error al procesar la venta en el servidor", ""
        except Exception as e:
            return False, f"Error de conexión: {e}", ""
