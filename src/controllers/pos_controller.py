from sqlalchemy.orm import Session
from src.models.models import Product, Sale, SaleDetail, Kardex, MovementType, PriceRule
from src.utils.event_bus import event_bus
import datetime

class POSController:
    def __init__(self, db: Session):
        self.db = db
        self.cart = [] # List of dicts

    def add_to_cart(self, sku_or_name: str, quantity: float, is_box: bool, product_id: int = None):
        """
        Busca producto y agrega al carrito.
        Retorna (Success: bool, Message: str)
        """
        product = None
        
        # Try finding by ID first if provided
        if product_id:
            product = self.db.query(Product).filter(Product.id == product_id, Product.is_active == True).first()
            
        # Try finding by SKU then Name if not found yet
        if not product:
            product = self.db.query(Product).filter(Product.sku == sku_or_name, Product.is_active == True).first()
        if not product:
            product = self.db.query(Product).filter(Product.name.ilike(f"%{sku_or_name}%"), Product.is_active == True).first()
        
        if not product:
            return False, "Producto no encontrado"

        # Determine units to deduct
        units_to_deduct = quantity
        price_to_use = product.price
        
        if is_box:
            if not product.is_box:
                return False, "Este producto no se vende por caja"
            units_to_deduct = quantity * product.conversion_factor
            price_to_use = product.price * product.conversion_factor

        # Check Stock
        if product.stock < units_to_deduct:
            return False, f"Stock insuficiente. Disponible: {product.stock} Unidades"

        # Check for Price Rules (Wholesale pricing)
        # Find the best matching rule: highest min_quantity that quantity meets
        applicable_rules = self.db.query(PriceRule).filter(
            PriceRule.product_id == product.id,
            PriceRule.min_quantity <= quantity
        ).order_by(PriceRule.min_quantity.desc()).all()
        
        if applicable_rules:
            # Use the first rule (highest min_quantity that applies)
            best_rule = applicable_rules[0]
            price_to_use = best_rule.price
            if is_box:
                price_to_use = best_rule.price * product.conversion_factor
        
        # Add to cart
        subtotal = price_to_use * quantity
        
        item = {
            "product_id": product.id,
            "name": product.name,
            "sku": product.sku,
            "quantity": quantity, # Qty of items (boxes or units)
            "units_deducted": units_to_deduct, # Real stock impact
            "unit_price": price_to_use, # Price of the item (box or unit)
            "subtotal": subtotal,
            "is_box": is_box,
            "unit_type": product.unit_type,  # NEW: Store unit type (Kg, Metro, etc.)
            "product_obj": product # Keep ref for finalization
        }
        
        self.cart.append(item)
        return True, "Agregado al carrito"

    def update_quantity(self, index: int, new_quantity: float):
        """
        Actualiza la cantidad de un item en el carrito.
        """
        if not (0 <= index < len(self.cart)):
            return False, "Item no válido"
            
        item = self.cart[index]
        product = item["product_obj"]
        
        # Recalculate units to deduct
        units_to_deduct = new_quantity
        if item["is_box"]:
            units_to_deduct = new_quantity * product.conversion_factor
            
        # Check Stock
        if product.stock < units_to_deduct:
            return False, f"Stock insuficiente. Disponible: {product.stock} Unidades"
        
        # Recalculate price based on new quantity (check price rules)
        price_to_use = product.price
        if item["is_box"]:
            price_to_use = product.price * product.conversion_factor
        
        # Check for Price Rules (Wholesale pricing)
        applicable_rules = self.db.query(PriceRule).filter(
            PriceRule.product_id == product.id,
            PriceRule.min_quantity <= new_quantity
        ).order_by(PriceRule.min_quantity.desc()).all()
        
        if applicable_rules:
            best_rule = applicable_rules[0]
            price_to_use = best_rule.price
            if item["is_box"]:
                price_to_use = best_rule.price * product.conversion_factor
            
        # Update item
        item["quantity"] = new_quantity
        item["units_deducted"] = units_to_deduct
        item["unit_price"] = price_to_use  # Update unit price
        item["subtotal"] = price_to_use * new_quantity
        
        return True, "Cantidad actualizada"

    def remove_from_cart(self, index: int):
        if 0 <= index < len(self.cart):
            self.cart.pop(index)

    def apply_discount(self, index: int, discount_value: float, discount_type: str):
        """
        Apply discount to a specific cart item.
        discount_type: 'PERCENT' or 'FIXED'
        """
        if not (0 <= index < len(self.cart)):
            return False, "Item no válido"
        
        item = self.cart[index]
        
        if discount_type == "PERCENT":
            if discount_value < 0 or discount_value > 100:
                return False, "El descuento debe estar entre 0 y 100%"
            discount_amount = (item["unit_price"] * item["quantity"]) * (discount_value / 100)
        elif discount_type == "FIXED":
            if discount_value < 0:
                return False, "El descuento no puede ser negativo"
            discount_amount = discount_value
        else:
            return False, "Tipo de descuento inválido"
        
        # Store discount info
        item["discount"] = discount_value
        item["discount_type"] = discount_type
        item["discount_amount"] = discount_amount
        
        # Recalculate subtotal
        original_subtotal = item["unit_price"] * item["quantity"]
        item["subtotal"] = max(0, original_subtotal - discount_amount)
        
        return True, f"Descuento aplicado: ${discount_amount:,.2f}"

    def apply_global_discount(self, discount_value: float, discount_type: str):
        """
        Apply discount to all items in cart proportionally.
        """
        if not self.cart:
            return False, "El carrito está vacío"
        
        total_before = self.get_total()
        
        if discount_type == "PERCENT":
            if discount_value < 0 or discount_value > 100:
                return False, "El descuento debe estar entre 0 y 100%"
            total_discount = total_before * (discount_value / 100)
        elif discount_type == "FIXED":
            if discount_value < 0:
                return False, "El descuento no puede ser negativo"
            if discount_value > total_before:
                return False, "El descuento no puede ser mayor al total"
            total_discount = discount_value
        else:
            return False, "Tipo de descuento inválido"
        
        # Apply proportionally to each item
        for item in self.cart:
            item_proportion = item["subtotal"] / total_before
            item_discount = total_discount * item_proportion
            
            item["discount"] = discount_value  # Store original value
            item["discount_type"] = discount_type
            item["discount_amount"] = item_discount
            
            original_subtotal = item["unit_price"] * item["quantity"]
            item["subtotal"] = max(0, original_subtotal - item_discount)
        
        return True, f"Descuento global aplicado: ${total_discount:,.2f}"

    def get_total(self):
        return sum(item["subtotal"] for item in self.cart)

    def finalize_sale(self, payments=None, customer_id=None, is_credit=False, currency="USD", exchange_rate=1.0, notes=""):
        """
        Finalize sale with support for mixed payments.
        
        Args:
            payments: List of dicts [{"method": "Efectivo Bs", "amount": 50, "currency": "Bs"}, ...]
                     If None, defaults to single payment with all methods combined
            customer_id: Optional customer ID
            is_credit: If True, sale is on credit (no payment required)
            currency: Currency of the sale (USD or Bs)
            exchange_rate: Exchange rate used
            notes: Optional notes
        """
        if not self.cart:
            return False, "El carrito está vacío", ""

        # If it's a cash sale (not credit), require open cash session
        if not is_credit:
            from src.models.models import CashSession
            session = self.db.query(CashSession).filter(CashSession.status == "OPEN").first()
            if not session:
                return False, "Debe abrir una sesión de caja antes de realizar ventas al contado", ""

        try:
            total = self.get_total()
            
            # Calculate total in Bs if currency is Bs
            total_bs = None
            if currency == "Bs":
                total_bs = total * exchange_rate
            
            # Validate payments if provided
            if not is_credit and payments:
                # Calculate total paid in USD (convert Bs payments to USD)
                total_paid_usd = 0
                for p in payments:
                    if p.get("currency") == "USD":
                        total_paid_usd += p["amount"]
                    else:  # Bs
                        total_paid_usd += p["amount"] / exchange_rate
                
                # Allow small rounding differences (0.01 USD)
                if abs(total_paid_usd - total) > 0.01:
                    return False, f"El total de pagos (${total_paid_usd:.2f}) no coincide con el total de la venta (${total:.2f})", ""
            
            # Determine payment_method string for backward compatibility
            if payments and len(payments) > 0:
                if len(payments) == 1:
                    payment_method = payments[0]["method"]
                else:
                    payment_method = "Pago Mixto"
            else:
                payment_method = "Efectivo USD"  # Default
            
            new_sale = Sale(
                total_amount=total, 
                payment_method=payment_method,
                customer_id=customer_id,
                is_credit=is_credit,
                paid=not is_credit,  # If credit, not paid yet
                currency=currency,
                exchange_rate_used=exchange_rate,
                total_amount_bs=total_bs,
                notes=notes if notes else None
            )
            self.db.add(new_sale)
            self.db.flush() # Get ID
            
            # Create SalePayment records if payments provided
            if payments and not is_credit:
                from src.models.models import SalePayment, CashMovement, CashSession
                
                # Get open cash session
                session = self.db.query(CashSession).filter(CashSession.status == "OPEN").first()
                if not session:
                    return False, "Debe abrir una sesión de caja antes de realizar ventas al contado", ""
                
                for payment in payments:
                    # Create SalePayment record
                    sale_payment = SalePayment(
                        sale_id=new_sale.id,
                        payment_method=payment["method"],
                        amount=payment["amount"],
                        currency=payment.get("currency", "Bs")
                    )
                    self.db.add(sale_payment)
                    


            # Get business name
            from src.controllers.config_controller import ConfigController
            config_ctrl = ConfigController(self.db)
            business_name = config_ctrl.get_config("BUSINESS_NAME", "FERRETERIA")

            ticket_lines = [
                f"=== {business_name} ===",
                f"Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
                f"Ticket #: {new_sale.id}",
                "-" * 20
            ]

            for item in self.cart:
                # Create Detail
                detail = SaleDetail(
                    sale_id=new_sale.id,
                    product_id=item["product_id"],
                    quantity=item["units_deducted"], # Store base units sold
                    unit_price=item["product_obj"].price, # Base unit price
                    discount=item.get("discount", 0.0),
                    discount_type=item.get("discount_type", "NONE"),
                    subtotal=item["subtotal"],
                    is_box_sale=item["is_box"]
                )
                self.db.add(detail)

                # Update Stock
                product = item["product_obj"]
                product.stock -= item["units_deducted"]
                
                # Kardex
                sale_type = "Crédito" if is_credit else "Contado"
                kardex = Kardex(
                    product_id=product.id,
                    movement_type=MovementType.SALE,
                    quantity=-item["units_deducted"],
                    balance_after=product.stock,
                    description=f"Venta Ticket #{new_sale.id} ({sale_type})"
                )
                self.db.add(kardex)
                
                # Register shrinkage if discount was applied
                if item.get("discount", 0) > 0:
                    # Calculate equivalent units of shrinkage
                    discount_amount = item["discount"]
                    unit_price = item["product_obj"].price
                    
                    if item["discount_type"] == "PERCENT":
                        # Percentage discount
                        shrinkage_value = item["subtotal"] * (discount_amount / 100)
                    else:
                        # Fixed discount
                        shrinkage_value = discount_amount
                    
                    # Convert to equivalent units
                    shrinkage_units = shrinkage_value / unit_price if unit_price > 0 else 0
                    
                    if shrinkage_units > 0:
                        shrinkage_kardex = Kardex(
                            product_id=product.id,
                            movement_type=MovementType.ADJUSTMENT,
                            quantity=-shrinkage_units,
                            balance_after=product.stock,
                            description=f"Merma por descuento en Venta #{new_sale.id} - ${shrinkage_value:.2f}"
                        )
                        self.db.add(shrinkage_kardex)

                # Ticket Line
                qty_display = f"{item['quantity']} {'CAJA' if item['is_box'] else 'UNID'}"
                ticket_lines.append(f"{item['name'][:15]} x {qty_display}")
                ticket_lines.append(f"   ${item['subtotal']:,.2f}")

            self.db.commit()
            
            # Emit signals
            event_bus.sales_updated.emit()
            event_bus.inventory_updated.emit()
            event_bus.products_updated.emit()
            
            ticket_lines.append("-" * 20)
            ticket_lines.append(f"TOTAL: ${total:,.2f}")
            
            # Add payment breakdown if mixed payments
            if payments and len(payments) > 1:
                ticket_lines.append("")
                ticket_lines.append("FORMA DE PAGO:")
                for p in payments:
                    ticket_lines.append(f"  {p['method']}: {p['amount']:.2f} {p.get('currency', 'Bs')}")
            
            ticket_lines.append("Gracias por su compra!")
            
            # Auto-print if enabled
            try:
                from src.controllers.printer_controller import PrinterController
                from src.controllers.config_controller import ConfigController
                
                config_ctrl = ConfigController(self.db)
                auto_print = config_ctrl.get_config("auto_print_tickets", "false")
                
                if auto_print == "true":
                    printer_ctrl = PrinterController(self.db)
                    try:
                        printer_ctrl.print_ticket(new_sale)
                    except Exception as print_error:
                        print(f"Auto-print error: {print_error}")
                        # Don't fail the sale if print fails
            except Exception as e:
                print(f"Printer module error: {e}")
            
            self.cart.clear()
            return True, "¡Venta Registrada Exitosamente!", "\n".join(ticket_lines)

        except Exception as e:
            self.db.rollback()
            return False, str(e), ""
