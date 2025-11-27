from sqlalchemy.orm import Session
from src.models.models import Product, Sale, SaleDetail, Kardex, MovementType, PriceRule
import datetime

class POSController:
    def __init__(self, db: Session):
        self.db = db
        self.cart = [] # List of dicts

    def add_to_cart(self, sku_or_name: str, quantity: float, is_box: bool):
        """
        Busca producto y agrega al carrito.
        Retorna (Success: bool, Message: str)
        """
        # Try finding by SKU first, then Name
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

    def get_total(self):
        return sum(item["subtotal"] for item in self.cart)

    def finalize_sale(self, payment_method="Efectivo USD", customer_id=None, is_credit=False, currency="USD", exchange_rate=1.0):
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
            
            new_sale = Sale(
                total_amount=total, 
                payment_method=payment_method,
                customer_id=customer_id,
                is_credit=is_credit,
                paid=not is_credit,  # If credit, not paid yet
                currency=currency,
                exchange_rate_used=exchange_rate,
                total_amount_bs=total_bs
            )
            self.db.add(new_sale)
            self.db.flush() # Get ID

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
                    quantity=item["units_deducted"], # Store base units sold? Or sold items?
                    # Usually for stats we want base units, but for receipt we want what user bought.
                    # Let's store base units in DB for consistency with stock, 
                    # but we might want to add a column 'display_quantity' later.
                    # For now, let's store 'quantity' as units_deducted (base units) to match Kardex logic easily.
                    unit_price=item["product_obj"].price, # Base unit price
                    subtotal=item["subtotal"],
                    is_box_sale=item["is_box"]
                )
                self.db.add(detail)

                # Update Stock
                product = item["product_obj"]
                product.stock -= item["units_deducted"]
                
                # Kardex
                kardex = Kardex(
                    product_id=product.id,
                    movement_type=MovementType.SALE,
                    quantity=-item["units_deducted"],
                    balance_after=product.stock,
                    description=f"Venta Ticket #{new_sale.id}"
                )
                self.db.add(kardex)

                # Ticket Line
                qty_display = f"{item['quantity']} {'CAJA' if item['is_box'] else 'UNID'}"
                ticket_lines.append(f"{item['name'][:15]} x {qty_display}")
                ticket_lines.append(f"   ${item['subtotal']:,.2f}")

            self.db.commit()
            
            ticket_lines.append("-" * 20)
            ticket_lines.append(f"TOTAL: ${total:,.2f}")
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
