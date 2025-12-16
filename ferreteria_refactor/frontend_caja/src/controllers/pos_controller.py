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

    def search_product_by_barcode(self, code):
        """
        Intelligent barcode search:
        1. Search in Product table by SKU
        2. If not found, search in ProductUnit table by barcode
        3. Calculate final price in Bs using default_rate_id
        
        Returns: dict with product info, unit details, and calculated prices
        """
        try:
            # Step 1: Search in Product table (by SKU)
            for product in self.cached_products:
                if product.get('sku') == code:
                    # Found in Product table - use base unit
                    return self._build_product_result(
                        product=product,
                        unit_name=product.get('base_unit', 'UNIDAD'),
                        conversion_factor=1.0,
                        unit_price=None,  # Use product price
                        barcode=code
                    )
            
            # Step 2: Search in ProductUnit table
            from frontend_caja.services.product_service import ProductService
            service = ProductService()
            
            # Get all product units and search by barcode
            for product in self.cached_products:
                try:
                    units = service.get_product_units(product['id'])
                    for unit in units:
                        if unit.get('barcode') == code and unit.get('is_active', True):
                            # Found in ProductUnit table
                            return self._build_product_result(
                                product=product,
                                unit_name=unit.get('name', 'Presentación'),
                                conversion_factor=unit.get('conversion_factor', 1.0),
                                unit_price=unit.get('price'),  # May be None
                                barcode=code,
                                unit_id=unit.get('id')
                            )
                except:
                    continue  # Skip if can't get units for this product
            
            return None  # Not found
            
        except Exception as e:
            print(f"Error in barcode search: {e}")
            return None
    
    def _build_product_result(self, product, unit_name, conversion_factor, unit_price, barcode, unit_id=None):
        """
        Build standardized product result with price calculations
        """
        # Determine base price (USD or base currency)
        if unit_price is not None and unit_price > 0:
            # Use specific unit price
            base_price_usd = unit_price
        else:
            # Use product price * conversion factor
            base_price_usd = product.get('price', 0) * conversion_factor
        
        # Get exchange rate for this product
        rate_info = self._get_exchange_rate_for_product(product)
        
        # Calculate price in Bs
        final_price_bs = base_price_usd * rate_info['rate_value']
        
        return {
            # Product info
            'product_id': product['id'],
            'name': product['name'],
            'sku': product.get('sku'),
            
            # Unit info
            'unit_name': unit_name,
            'unit_id': unit_id,
            'conversion_factor': conversion_factor,
            'barcode': barcode,
            
            # Pricing
            'base_price_usd': base_price_usd,
            'rate_name': rate_info['rate_name'],
            'rate_value': rate_info['rate_value'],
            'final_price_bs': final_price_bs,
            
            # Stock info
            'stock': product.get('stock', 0),
            'location': product.get('location'),
            
            # Full product object for compatibility
            'product_obj': product
        }
    
    def _get_exchange_rate_for_product(self, product):
        """
        Get exchange rate for a product based on its default_rate_id
        Returns dict with rate_name and rate_value
        """
        try:
            from src.controllers.config_controller import ConfigController
            config_controller = ConfigController()
            
            # Get product's default rate
            default_rate_id = product.get('default_rate_id')
            
            if default_rate_id:
                # Get all rates and find the one we need
                rates = config_controller.get_exchange_rates()
                for rate in rates:
                    if rate.get('id') == default_rate_id and rate.get('is_active', True):
                        return {
                            'rate_name': rate.get('name', 'Tasa'),
                            'rate_value': rate.get('rate', 1.0)
                        }
            
            # Fallback: get operating currency rate or 1:1
            operating_currency = config_controller.get_config('OPERATING_CURRENCY', 'VES')
            
            if operating_currency != 'USD':
                # Try to get a rate for operating currency
                rates = config_controller.get_exchange_rates()
                for rate in rates:
                    if rate.get('currency_code') == operating_currency and rate.get('is_active', True):
                        return {
                            'rate_name': rate.get('name', 'Estándar'),
                            'rate_value': rate.get('rate', 1.0)
                        }
            
            # Ultimate fallback
            return {'rate_name': 'Estándar (1:1)', 'rate_value': 1.0}
            
        except Exception as e:
            print(f"Error getting exchange rate: {e}")
            return {'rate_name': 'Estándar (1:1)', 'rate_value': 1.0}

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

    def add_to_cart(self, sku_or_name: str, quantity: float, is_box: bool, product_id: int = None, price_tier: str = "price", unit_data: dict = None):
        """
        Refactored add_to_cart to use cached product list from API.
        price_tier: 'price' (default), 'price_mayor_1', 'price_mayor_2'
        unit_data: Optional dict with specific unit details (if selection made)
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

        # === AMBIGUITY CHECK (Only if not box mode and no specific unit data provided) ===
        if not is_box and not unit_data:
            # Check for active units
            try:
                # We need to fetch units. Note: This might be slow if we do it for every scan, 
                # but essential for this feature.
                units = self.product_service.get_product_units(product['id'])
                active_units = [u for u in units if u.get('is_active', True)]
                
                if active_units:
                    # AMBIGUITY DETECTED -> Signal View to show dialog
                    # We return a special payload dictionary as second argument instead of message string
                    return False, {
                        'status': 'SELECTION_NEEDED',
                        'product': product,
                        'units': active_units
                    }
            except Exception as e:
                print(f"Error checking units: {e}")
                # Continue as normal if error (fail safe to base unit)

        # === PRICING & UNIT LOGIC ===
        
        # Default numeric values
        conversion_factor = 1.0
        unit_name = product.get('base_unit', 'UNIDAD')
        base_price_usd = product.get(price_tier, product['price'])
        # Handle 0 price in tier
        if base_price_usd == 0 and price_tier != "price":
             base_price_usd = product['price']

        # If specific unit was selected (from Dialog)
        if unit_data:
            unit_name = unit_data.get('unit_name')
            conversion_factor = unit_data.get('conversion_factor', 1.0)
            
            # Using specific unit price if set, otherwise Base * Factor
            spec_price = unit_data.get('price')
            if spec_price and spec_price > 0:
                 # If unit has specific price, use it (override tier? specific usually overrides)
                 base_price_usd = spec_price
            else:
                 # Recalculate base price based on factor
                 base_price_usd = base_price_usd * conversion_factor
                 
            # Note: Tiers (Mayorista) usually apply to base unit.
            # If selling a Sack (Factor 50), Mayorista Price * 50 ??
            # Yes, usually.
        
        elif is_box:
             # Legacy Box Mode logic (F2) 
             conversion_factor = product.get('conversion_factor', 1) # This is usually 'main_provider_factor' in legacy
             # Box usually implies multiplied price
             base_price_usd = base_price_usd * conversion_factor
             unit_name = "CAJA/PAQUETE" # generic name if not specific unit

        # Validate Price
        unit_price = base_price_usd # Final unit price to charge
        
        units_to_deduct = quantity * conversion_factor

        subtotal = unit_price * quantity
        
        # Determine Rate
        rate_info = self._get_exchange_rate_for_product(product)
        
        # Calculate BSF values
        final_price_bs = unit_price * rate_info['rate_value']
        subtotal_bs = subtotal * rate_info['rate_value']
        
        item = {
            "product_id": product['id'],
            "name": product['name'],
            "sku": product.get('sku'),
            "quantity": quantity,
            "units_deducted": units_to_deduct,
            "unit_price": unit_price, # USD
            "base_price_usd": unit_price,
            "subtotal": subtotal,
            "is_box": is_box,
            "unit_type": product.get("unit_type", "Unidad"), # Legacy field
            "unit_name": unit_name, # New field
            "unit_id": unit_data.get('unit_id') if unit_data else None,
            "img_url": product.get('image_url'),
            "location": product.get("location"),
            "price_tier": price_tier, 
            "product_obj": product,
            "conversion_factor": conversion_factor,
            "rate_name": rate_info['rate_name'],
            "rate_value": rate_info['rate_value'],
            "final_price_bs": final_price_bs,
            "subtotal_bs": subtotal_bs
        }
        
        self.cart.append(item)
        return True, "Agregado al carrito"
    
    def add_to_cart_from_barcode(self, barcode: str, quantity: float = 1.0):
        """
        Add product to cart using barcode search (supports ProductUnit barcodes)
        """
        product_result = self.search_product_by_barcode(barcode)
        
        if not product_result:
            return False, "Código de barras no encontrado"
        
        # Extract data
        conversion_factor = product_result['conversion_factor']
        base_price_usd = product_result['base_price_usd']
        rate_value = product_result['rate_value']
        final_price_bs = product_result['final_price_bs']
        
        # Calculate
        subtotal_usd = base_price_usd * quantity
        subtotal_bs = final_price_bs * quantity
        units_to_deduct = quantity * conversion_factor
        
        # Build cart item
        item = {
            "product_id": product_result['product_id'],
            "name": product_result['name'],
            "sku": product_result.get('sku'),
            "barcode": barcode,
            "unit_name": product_result['unit_name'],
            "unit_id": product_result.get('unit_id'),
            "conversion_factor": conversion_factor,
            "quantity": quantity,
            "units_deducted": units_to_deduct,
            "base_price_usd": base_price_usd,
            "unit_price": base_price_usd,
            "subtotal": subtotal_usd,
            "rate_name": product_result['rate_name'],
            "rate_value": rate_value,
            "final_price_bs": final_price_bs,
            "subtotal_bs": subtotal_bs,
            "is_box": False,
            "unit_type": product_result['unit_name'],
            "location": product_result.get('location'),
            "price_tier": "price",
            "product_obj": product_result.get('product_obj')
        }
        
        self.cart.append(item)
        return True, f"Agregado: {product_result['name']} - {product_result['unit_name']}"

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
            # CRITICAL: Get conversion factor for correct stock deduction
            # Example: 1 Saco (factor 42.5) will deduct 42.5 kg from stock
            conversion_factor = item.get("conversion_factor", 1.0)
            
            sale_payload["items"].append({
                "product_id": item["product_id"],
                "quantity": item["quantity"],  # Quantity of presentations sold
                "conversion_factor": conversion_factor,  # Units per presentation
                "is_box": item.get("is_box", False),
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
