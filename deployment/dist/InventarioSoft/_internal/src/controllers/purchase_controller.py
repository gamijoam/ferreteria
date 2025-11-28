from sqlalchemy.orm import Session
from src.models.models import PurchaseOrder, PurchaseOrderDetail, Product, Kardex, MovementType
import datetime

class PurchaseController:
    def __init__(self, db: Session):
        self.db = db

    def create_purchase_order(self, supplier_id, items, expected_delivery=None, notes=None):
        """
        Create a new purchase order
        items: list of dicts with {product_id, quantity, unit_cost}
        """
        try:
            # Calculate total
            total = sum(item['quantity'] * item['unit_cost'] for item in items)
            
            # Create order
            order = PurchaseOrder(
                supplier_id=supplier_id,
                total_amount=total,
                expected_delivery=expected_delivery,
                notes=notes
            )
            self.db.add(order)
            self.db.flush()  # Get order ID
            
            # Create details
            for item in items:
                detail = PurchaseOrderDetail(
                    order_id=order.id,
                    product_id=item['product_id'],
                    quantity=item['quantity'],
                    unit_cost=item['unit_cost'],
                    subtotal=item['quantity'] * item['unit_cost']
                )
                self.db.add(detail)
            
            self.db.commit()
            self.db.refresh(order)
            return order, None
        except Exception as e:
            self.db.rollback()
            return None, str(e)

    def get_all_purchase_orders(self, status=None):
        """Get all purchase orders, optionally filtered by status"""
        query = self.db.query(PurchaseOrder)
        if status:
            query = query.filter(PurchaseOrder.status == status)
        return query.order_by(PurchaseOrder.order_date.desc()).all()

    def get_purchase_order(self, order_id):
        """Get purchase order by ID"""
        return self.db.query(PurchaseOrder).get(order_id)

    def receive_purchase_order(self, order_id, user_id):
        """
        Receive a purchase order:
        - Update product stock
        - Update product cost_price
        - Create Kardex entries
        - Mark order as RECEIVED
        """
        order = self.get_purchase_order(order_id)
        if not order:
            return False, "Orden no encontrada"
        
        if order.status != "PENDING":
            return False, f"La orden ya está en estado: {order.status}"
        
        try:
            for detail in order.details:
                product = self.db.query(Product).get(detail.product_id)
                if not product:
                    continue
                
                # Update stock
                old_stock = product.stock
                product.stock += detail.quantity
                
                # Update cost_price with weighted average
                if product.cost_price == 0:
                    # First time setting cost
                    product.cost_price = detail.unit_cost
                else:
                    # Weighted average: (old_cost * old_qty + new_cost * new_qty) / total_qty
                    total_value = (product.cost_price * old_stock) + (detail.unit_cost * detail.quantity)
                    product.cost_price = total_value / product.stock
                
                # Create Kardex entry
                kardex = Kardex(
                    product_id=product.id,
                    movement_type=MovementType.PURCHASE,
                    quantity=detail.quantity,
                    balance_after=product.stock,
                    description=f"Recepción OC #{order.id} - {order.supplier.name}"
                )
                self.db.add(kardex)
            
            # Mark order as received
            order.status = "RECEIVED"
            order.received_date = datetime.datetime.utcnow()
            order.received_by = user_id
            
            self.db.commit()
            return True, "Orden recibida correctamente. Stock e inventario actualizados."
        except Exception as e:
            self.db.rollback()
            return False, str(e)

    def cancel_purchase_order(self, order_id):
        """Cancel a purchase order"""
        order = self.get_purchase_order(order_id)
        if not order:
            return False, "Orden no encontrada"
        
        if order.status == "RECEIVED":
            return False, "No se puede cancelar una orden ya recibida"
        
        try:
            order.status = "CANCELLED"
            self.db.commit()
            return True, "Orden cancelada"
        except Exception as e:
            self.db.rollback()
            return False, str(e)
