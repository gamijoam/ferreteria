from sqlalchemy.orm import Session
from src.models.models import Product

class LabelController:
    def __init__(self, db: Session):
        self.db = db

    def generate_label_text(self, product_id: int, quantity: int):
        """Generate text for N labels"""
        product = self.db.query(Product).get(product_id)
        if not product:
            raise ValueError("Producto no encontrado")
        
        labels = []
        for i in range(quantity):
            label = [
                "=" * 30,
                f"{product.name}",
                "-" * 30,
                f"Precio: ${product.price:,.2f}",
                f"SKU: {product.sku or 'N/A'}",
                "=" * 30,
                ""
            ]
            labels.append("\n".join(label))
        
        return "\n".join(labels)
