from sqlalchemy.orm import Session
from src.models.models import Sale, SaleDetail, Return, ReturnDetail, Product, Kardex, MovementType, CashSession, CashMovement
import datetime

class ReturnController:
    def __init__(self, db: Session):
        self.db = db

    def find_sale(self, sale_id: int):
        return self.db.query(Sale).filter(Sale.id == sale_id).first()

    def process_return(self, sale_id: int, items_to_return: list, reason: str):
        """
        items_to_return: List of dicts {product_id, quantity}
        """
        sale = self.find_sale(sale_id)
        if not sale:
            raise ValueError("Venta no encontrada")

        # Calculate total refund
        total_refund = 0
        
        # Create Return Record
        new_return = Return(
            sale_id=sale.id,
            total_refunded=0, # Will update later
            reason=reason
        )
        self.db.add(new_return)
        self.db.flush() # Get ID

        for item in items_to_return:
            product_id = item['product_id']
            qty_return = item['quantity']
            
            if qty_return <= 0:
                continue

            # Find original sale detail to get price
            # Note: A sale might have multiple lines for same product (unlikely but possible).
            # We take the first matching one or sum them up. For simplicity, we assume unique product per sale.
            detail = self.db.query(SaleDetail).filter(
                SaleDetail.sale_id == sale.id, 
                SaleDetail.product_id == product_id
            ).first()
            
            if not detail:
                raise ValueError(f"Producto {product_id} no pertenece a esta venta")
            
            # Validation: Cannot return more than sold? 
            # Ideally we should check if already returned previously.
            # For this MVP, we just check against original qty.
            if qty_return > detail.quantity:
                 raise ValueError(f"No puedes devolver más de lo comprado ({detail.quantity})")

            # Calculate refund amount for this item
            # Price per unit * qty
            refund_amount = detail.unit_price * qty_return
            total_refund += refund_amount

            # Create Return Detail
            ret_detail = ReturnDetail(
                return_id=new_return.id,
                product_id=product_id,
                quantity=qty_return
            )
            self.db.add(ret_detail)

            # 1. Restore Stock
            product = self.db.query(Product).get(product_id)
            product.stock += qty_return

            # 2. Kardex Entry
            kardex = Kardex(
                product_id=product.id,
                movement_type=MovementType.RETURN,
                quantity=qty_return,
                balance_after=product.stock,
                description=f"Devolución Venta #{sale.id}"
            )
            self.db.add(kardex)

        new_return.total_refunded = total_refund

        # 3. Cash Impact (Refund)
        # Check if session is open
        session = self.db.query(CashSession).filter(CashSession.status == "OPEN").first()
        if session:
            cash_movement = CashMovement(
                session_id=session.id,
                type="EXPENSE", # Refund is an expense/withdrawal
                amount=total_refund,
                description=f"Devolución Venta #{sale.id}: {reason}"
            )
            self.db.add(cash_movement)
        
        self.db.commit()
        return new_return
