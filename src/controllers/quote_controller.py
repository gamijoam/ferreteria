from sqlalchemy.orm import Session
from src.models.models import Quote, QuoteDetail, Product
import datetime

class QuoteController:
    def __init__(self, db: Session):
        self.db = db

    def save_quote(self, cart: list, customer_id=None, notes=""):
        """Save current cart as a quote"""
        if not cart:
            raise ValueError("El carrito está vacío")
        
        total = sum(item["subtotal"] for item in cart)
        
        new_quote = Quote(
            customer_id=customer_id,
            total_amount=total,
            notes=notes
        )
        self.db.add(new_quote)
        self.db.flush()
        
        for item in cart:
            detail = QuoteDetail(
                quote_id=new_quote.id,
                product_id=item["product_id"],
                quantity=item["quantity"],
                unit_price=item["unit_price"],
                subtotal=item["subtotal"],
                is_box_sale=item["is_box"]
            )
            self.db.add(detail)
        
        self.db.commit()
        return new_quote

    def get_all_quotes(self, status=None):
        """Get all quotes, optionally filtered by status"""
        query = self.db.query(Quote)
        if status:
            query = query.filter(Quote.status == status)
        return query.order_by(Quote.date.desc()).all()

    def get_quote_details(self, quote_id: int):
        """Get quote with details"""
        return self.db.query(Quote).filter(Quote.id == quote_id).first()

    def convert_to_cart(self, quote_id: int):
        """Convert quote to cart format for POS"""
        quote = self.get_quote_details(quote_id)
        if not quote:
            raise ValueError("Cotización no encontrada")
        
        if quote.status == "CONVERTED":
            raise ValueError("Esta cotización ya fue convertida a venta")
        
        cart = []
        for detail in quote.details:
            product = detail.product
            
            # Reconstruct cart item
            item = {
                "product_id": product.id,
                "name": product.name,
                "sku": product.sku,
                "quantity": detail.quantity,
                "units_deducted": detail.quantity,  # Simplified, assumes units
                "unit_price": detail.unit_price,
                "subtotal": detail.subtotal,
                "is_box": detail.is_box_sale,
                "product_obj": product
            }
            cart.append(item)
        
        return cart

    def mark_as_converted(self, quote_id: int):
        """Mark quote as converted to sale"""
        quote = self.db.query(Quote).get(quote_id)
        if quote:
            quote.status = "CONVERTED"
            self.db.commit()

    def generate_quote_text(self, quote_id: int):
        """Generate printable quote text"""
        quote = self.get_quote_details(quote_id)
        if not quote:
            return ""
        
        lines = [
            "=" * 40,
            "COTIZACIÓN",
            "=" * 40,
            f"Número: {quote.id}",
            f"Fecha: {quote.date.strftime('%Y-%m-%d %H:%M')}",
            f"Cliente: {quote.customer.name if quote.customer else 'N/A'}",
            "-" * 40,
            ""
        ]
        
        for detail in quote.details:
            tipo = "CAJA" if detail.is_box_sale else "UNID"
            lines.append(f"{detail.product.name}")
            lines.append(f"  {detail.quantity} {tipo} x ${detail.unit_price:,.2f} = ${detail.subtotal:,.2f}")
        
        lines.extend([
            "",
            "-" * 40,
            f"TOTAL: ${quote.total_amount:,.2f}",
            "",
            f"Notas: {quote.notes or 'N/A'}",
            "",
            "Esta cotización es válida por 30 días.",
            "=" * 40
        ])
        
        return "\n".join(lines)
