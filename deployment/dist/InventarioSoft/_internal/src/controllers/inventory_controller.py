from sqlalchemy.orm import Session
from src.models.models import Product, Kardex, MovementType

class InventoryController:
    def __init__(self, db: Session):
        self.db = db

    def add_stock(self, product_id: int, quantity: int, is_box_input: bool, description: str = "Compra"):
        """
        Registra una entrada de mercancía (Compra).
        Maneja la conversión automática de Cajas a Unidades.
        """
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError("Producto no encontrado")

        # Calcular unidades totales
        total_units = quantity
        
        # Si la entrada es "por caja", multiplicamos por el factor del producto
        # OJO: Si el producto NO es caja (is_box=False), ignoramos is_box_input o lanzamos error.
        # Asumiremos que si el usuario marca "Es Caja" en la entrada, confía en el factor del producto.
        if is_box_input and product.is_box:
            total_units = quantity * product.conversion_factor
            description += f" (Entrada: {quantity} Cajas x {product.conversion_factor})"
        else:
            description += f" (Entrada: {quantity} Unidades)"

        # Actualizar Stock
        product.stock += total_units
        
        # Crear Kardex
        kardex_entry = Kardex(
            product_id=product.id,
            movement_type=MovementType.PURCHASE,
            quantity=total_units,
            balance_after=product.stock,
            description=description
        )
        
        self.db.add(kardex_entry)
        self.db.commit()
        self.db.refresh(product)
        return product

    def remove_stock(self, product_id: int, quantity: float, description: str = "Ajuste de Salida"):
        """
        Registra una salida de mercancía (Ajuste / Merma / Donación).
        """
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError("Producto no encontrado")

        if product.stock < quantity:
            raise ValueError(f"Stock insuficiente. Stock actual: {product.stock}")

        # Actualizar Stock
        product.stock -= quantity
        
        # Crear Kardex
        kardex_entry = Kardex(
            product_id=product.id,
            movement_type=MovementType.ADJUSTMENT_OUT,
            quantity=quantity,
            balance_after=product.stock,
            description=description
        )
        
        self.db.add(kardex_entry)
        self.db.commit()
        self.db.refresh(product)
        return product

    def get_kardex(self, product_id: int = None):
        query = self.db.query(Kardex).join(Product)
        
        if product_id:
            query = query.filter(Kardex.product_id == product_id)
            
        return query.order_by(Kardex.date.desc()).all()
