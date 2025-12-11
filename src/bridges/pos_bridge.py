"""
POSBridge.py - Python-QML Bridge for Point of Sale
Exposes POS functionality to QML layer
"""
from PySide6.QtCore import QObject, Signal, Slot, Property
from sqlalchemy import text
from database.db import SessionLocal
from controllers.pos_controller import POSController
from controllers.customer_controller import CustomerController
from controllers.config_controller import ConfigController


class POSBridge(QObject):
    """Bridge between QML and Python POS logic"""
    
    # Signals to QML
    cartUpdated = Signal()
    saleCompleted = Signal(int, str)  # sale_id, ticket
    saleError = Signal(str)
    exchangeRateChanged = Signal(float)
    
    def __init__(self):
        super().__init__()
        self.db = SessionLocal()
        self.pos_controller = POSController(self.db)
        self.customer_controller = CustomerController(self.db)
        self.config_controller = ConfigController(self.db)
        
        # Load exchange rate
        self._exchange_rate = self.config_controller.get_exchange_rate()
        
    @Property(float, notify=exchangeRateChanged)
    def exchangeRate(self):
        """Get current exchange rate"""
        return self._exchange_rate
    
    @Property(list, notify=cartUpdated)
    def cart(self):
        """Get current cart items as list of dicts"""
        return self.pos_controller.cart
    
    @Property(float, notify=cartUpdated)
    def total(self):
        """Get cart total in USD"""
        return self.pos_controller.get_total()
    
    @Property(float, notify=cartUpdated)
    def totalBs(self):
        """Get cart total in Bs"""
        return self.pos_controller.get_total() * self._exchange_rate
    
    @Slot(str, float, bool, int)
    def addToCart(self, sku_or_name: str, quantity: float, is_box: bool, product_id: int = 0):
        """
        Add product to cart
        
        Args:
            sku_or_name: Product SKU or name
            quantity: Quantity to add
            is_box: True if selling by box
            product_id: Product ID (optional)
        """
        pid = product_id if product_id > 0 else None
        success, msg = self.pos_controller.add_to_cart(sku_or_name, quantity, is_box, pid)
        
        if success:
            self.cartUpdated.emit()
        else:
            self.saleError.emit(msg)
    
    @Slot(int, float)
    def updateQuantity(self, index: int, new_quantity: float):
        """
        Update quantity of cart item
        
        Args:
            index: Cart item index
            new_quantity: New quantity
        """
        success, msg = self.pos_controller.update_quantity(index, new_quantity)
        
        if success:
            self.cartUpdated.emit()
        else:
            self.saleError.emit(msg)
    
    @Slot(int)
    def removeFromCart(self, index: int):
        """
        Remove item from cart
        
        Args:
            index: Cart item index
        """
        self.pos_controller.remove_from_cart(index)
        self.cartUpdated.emit()
    
    @Slot()
    def clearCart(self):
        """Clear entire cart"""
        self.pos_controller.cart.clear()
        self.cartUpdated.emit()
    
    @Slot(int, float, str)
    def applyItemDiscount(self, index: int, value: float, discount_type: str):
        """
        Apply discount to specific item
        
        Args:
            index: Cart item index
            value: Discount value
            discount_type: "PERCENT" or "FIXED"
        """
        success, msg = self.pos_controller.apply_discount(index, value, discount_type)
        
        if success:
            self.cartUpdated.emit()
        else:
            self.saleError.emit(msg)
    
    @Slot(float, str)
    def applyGlobalDiscount(self, value: float, discount_type: str):
        """
        Apply discount to entire cart
        
        Args:
            value: Discount value
            discount_type: "PERCENT" or "FIXED"
        """
        success, msg = self.pos_controller.apply_global_discount(value, discount_type)
        
        if success:
            self.cartUpdated.emit()
        else:
            self.saleError.emit(msg)
    
    @Slot(str, result=list)
    def searchProducts(self, query: str):
        """
        Search products by name or SKU
        
        Args:
            query: Search query
            
        Returns:
            List of product dicts with name, sku, price, stock, location
        """
        if len(query) < 2:
            return []
        
        # Create a fresh session for this query to avoid transaction issues
        search_db = SessionLocal()
        
        try:
            # Use raw SQL to avoid importing Product model multiple times
            sql = text("""
                SELECT id, name, sku, price, stock, location, unit_type, is_box
                FROM products
                WHERE is_active = true
                AND (name ILIKE :query OR sku ILIKE :query)
                LIMIT 20
            """)
            
            result = search_db.execute(sql, {"query": f"%{query}%"})
            
            results = []
            for row in result:
                results.append({
                    "id": row[0],
                    "name": row[1],
                    "sku": row[2] or "",
                    "price": float(row[3]),
                    "stock": float(row[4]),
                    "location": row[5] or "",
                    "unit_type": row[6] or "Unidad",
                    "is_box": bool(row[7])
                })
            
            return results
        except Exception as e:
            print(f"Error searching products: {e}")
            search_db.rollback()
            return []
        finally:
            search_db.close()
    
    @Slot(str, result=list)
    def searchCustomers(self, query: str):
        """
        Search customers by name or ID number
        
        Args:
            query: Search query
            
        Returns:
            List of customer dicts
        """
        if len(query) < 2:
            return []
        
        # Create a fresh session for this query
        search_db = SessionLocal()
        
        try:
            # Use customer controller with fresh session
            from controllers.customer_controller import CustomerController
            customer_ctrl = CustomerController(search_db)
            customers = customer_ctrl.search_customers(query)
            
            results = []
            for c in customers:
                results.append({
                    "id": c.id,
                    "name": c.name,
                    "id_number": c.id_number or "",
                    "phone": c.phone or "",
                    "balance": float(c.balance) if hasattr(c, 'balance') else 0.0
                })
            
            return results
        except Exception as e:
            print(f"Error searching customers: {e}")
            search_db.rollback()
            return []
        finally:
            search_db.close()
    
    @Slot(list, int, bool)
    def finalizeSale(self, payments, customer_id: int, is_credit: bool):
        """
        Process the sale
        
        Args:
            payments: List of payment dicts [{method, amount, currency}, ...]
            customer_id: Customer ID (0 if none)
            is_credit: True if credit sale
        """
        # Convert QML list to Python list
        payment_list = []
        if payments and not is_credit:
            for p in payments:
                payment_list.append({
                    "method": p["method"],
                    "amount": float(p["amount"]),
                    "currency": p["currency"]
                })
        
        # Convert customer_id (0 means None)
        cust_id = customer_id if customer_id > 0 else None
        
        success, msg, ticket = self.pos_controller.finalize_sale(
            payments=payment_list if payment_list else None,
            customer_id=cust_id,
            is_credit=is_credit,
            currency="USD",
            exchange_rate=self._exchange_rate,
            notes=""
        )
        
        if success:
            # Extract sale ID from ticket (first line after "Ticket #:")
            sale_id = 0
            for line in ticket.split('\n'):
                if 'Ticket #:' in line:
                    try:
                        sale_id = int(line.split(':')[1].strip())
                    except:
                        pass
                    break
            
            self.saleCompleted.emit(sale_id, ticket)
            self.cartUpdated.emit()
        else:
            self.saleError.emit(msg)

    @Slot(int, result=list)
    def getPickingItems(self, sale_id: int):
        """Get items for picking list [name, quantity, location, is_box]"""
        session = SessionLocal()
        session = SessionLocal()
        try:
            # Use raw SQL to avoid metadata conflict with imports
            sql = text("""
                SELECT p.name, sd.quantity, sd.is_box_sale, p.location
                FROM sale_details sd
                JOIN products p ON sd.product_id = p.id
                WHERE sd.sale_id = :sale_id
            """)
            
            result = session.execute(sql, {"sale_id": sale_id})
            
            results = []
            for row in result:
                results.append({
                    "name": row[0],
                    "quantity": float(row[1]),
                    "is_box": bool(row[2]),
                    "location": row[3] or "-"
                })
            return results
        except Exception as e:
            print(f"Error getting picking items: {e}")
            return []
        finally:
            session.close()

    def __del__(self):
        """Cleanup database connection"""
        if hasattr(self, 'db'):
            self.db.close()
