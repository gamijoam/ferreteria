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

    def get_applicable_price(self, product, quantity, is_box, price_tier="price"):
        """
        Calculate unit price based on tier and volume rules.
        Returns final unit price (per item added, e.g. per box if is_box).
        """
        # 1. Base Price from Tier
        base_price = product.get(price_tier, product['price'])
        if base_price == 0 and price_tier != "price":
             base_price = product['price']
        
        unit_price = base_price
        
        # 2. Check Automatic Rules ONLY if tier is default
        # Rules are assumed to be per base unit
        if price_tier == "price" and product.get('price_rules'):
            total_units = quantity * (product.get('conversion_factor', 1) if is_box else 1)
            
            applicable_rules = [
                r for r in product['price_rules'] 
                if total_units >= r['min_quantity']
            ]
            
            if applicable_rules:
                # Pick rule with highest min_quantity (closest tier reached)
                best_rule = max(applicable_rules, key=lambda x: x['min_quantity'])
                unit_price = best_rule['price']
        
        # 3. Apply Box Factor for final display price
        final_price = unit_price
        if is_box:
             final_price = unit_price * product.get('conversion_factor', 1)
             
        return final_price

    def add_to_cart(self, sku_or_name: str, quantity: float, is_box: bool, product_id: int = None, price_tier: str = "price"):
        """
        Refactored add_to_cart to use cached product list from API.
        price_tier: 'price' (default), 'price_mayor_1', 'price_mayor_2'
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

        # Pricing Logic
        price_to_use = self.get_applicable_price(product, quantity, is_box, price_tier)
        
        units_to_deduct = quantity
        if is_box:
             units_to_deduct = quantity * product['conversion_factor']

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
            "location": product.get("location"),
            "price_tier": price_tier, # Store tier for updates
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

    def update_quantity(self, index: int, new_quantity: float):
        """Update quantity of item in cart"""
        if not (0 <= index < len(self.cart)):
             return False, "Ítem inválido"
             
        if new_quantity <= 0:
             return False, "Cantidad debe ser mayor a 0"
             
        # Recalculate
        item = self.cart[index]
        product = item['product_obj']
        is_box = item['is_box']
        price_tier = item.get('price_tier', 'price')
        
        price_to_use = self.get_applicable_price(product, new_quantity, is_box, price_tier)
        
        units_to_deduct = new_quantity
        if is_box:
             units_to_deduct = new_quantity * product.get('conversion_factor', 1)
             
        item['quantity'] = new_quantity
        item['units_deducted'] = units_to_deduct
        item['unit_price'] = price_to_use # Update unit price if rule changed
        item['subtotal'] = price_to_use * new_quantity
        
        return True, "Cantidad actualizada"

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
        # Build payload matching schemas.SaleCreate
        
        # Build payload matching schemas.SaleCreate
        
        # Determine main method and payments list
        payment_list_payload = []
        main_method = "Efectivo"
        if payments:
            main_method = payments[0]["method"] if len(payments) == 1 else "Mixto"
            for p in payments:
                payment_list_payload.append({
                    "amount": p["amount"],
                    "currency": p["currency"],
                    "payment_method": p["method"], # Map frontend 'method' to backend 'payment_method'
                    "exchange_rate": exchange_rate # Assuming current rate for all
                })
        
        # IMPORTANT: 'total_amount' in SaleCreate is the INVOICE TOTAL.
        # But 'payments' tracking handles the cash.
        # We send the invoice total in the header currency (e.g. USD usually)
        
        sale_payload = {
            "customer_id": customer_id,
            "payment_method": main_method,
            "total_amount": total, # Invoice total in USD (or base currency)
            "currency": currency,
            "exchange_rate": exchange_rate,
            "notes": notes,
            "is_credit": is_credit, # Passed from argument
            "items": [],
            "payments": payment_list_payload
        }

        for item in self.cart:
            sale_payload["items"].append({
                "product_id": item["product_id"],
                "quantity": item["quantity"], 
                "is_box": item["is_box"],
                # Assuming cart items might have discount info in future refactor
                "discount": item.get("discount", 0.0),
                "discount_type": item.get("discount_type", "NONE")
            })

        # Call Service
        print(f"Sending sale to API (Total: {total})...")
        try:
            result = self.product_service.record_sale(sale_payload)
            
            if result and result.get("status") == "success":
                sale_id = result.get("sale_id")
                ticket = f"Venta #{sale_id} Exitosa!\nTotal: ${total:,.2f}\n(Procesado por API)"
                self.cart.clear()
                self.reload_products() 
                return True, "¡Venta Registrada!", ticket
            else:
                return False, "Error al procesar la venta en el servidor", ""
        except Exception as e:
            return False, f"Error de conexión: {e}", ""
