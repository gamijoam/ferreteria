from sqlalchemy.orm import Session
from src.models.models import Product, Kardex, MovementType
import datetime

class ProductController:
    def __init__(self, db: Session):
        self.db = db

    def create_product(self, name, sku, price, cost_price, stock, min_stock, is_box, conversion_factor, unit_type, category_id=None, supplier_id=None):
        """Create a new product"""
        # Check if SKU exists and is active
        if sku:
            existing = self.db.query(Product).filter(Product.sku == sku).first()
            if existing:
                raise ValueError(f"El SKU '{sku}' ya existe.")

        new_product = Product(
            name=name,
            sku=sku,
            price=price,
            cost_price=cost_price,
            stock=stock,
            min_stock=min_stock,
            is_box=is_box,
            conversion_factor=conversion_factor,
            unit_type=unit_type,
            category_id=category_id,
            supplier_id=supplier_id,
            is_active=True
        )
        self.db.add(new_product)
        self.db.commit()
        return new_product

    def update_product(self, product_id, name, sku, price, cost_price, stock, min_stock, is_box, conversion_factor, unit_type, category_id=None, supplier_id=None):
        """Update an existing product"""
        product = self.db.query(Product).get(product_id)
        if not product:
            raise ValueError("Producto no encontrado")

        # Check SKU uniqueness if changed
        if sku and sku != product.sku:
            existing = self.db.query(Product).filter(Product.sku == sku, Product.id != product_id).first()
            if existing:
                raise ValueError(f"El SKU '{sku}' ya está en uso por otro producto.")

        # Check for stock change and log to Kardex
        if stock != product.stock:
            diff = stock - product.stock
            # Use ADJUSTMENT_IN for increases, ADJUSTMENT_OUT for decreases
            movement_type = MovementType.ADJUSTMENT_IN if diff > 0 else MovementType.ADJUSTMENT_OUT
            kardex_entry = Kardex(
                product_id=product.id,
                movement_type=movement_type,
                quantity=diff,
                balance_after=stock,
                description="Ajuste manual en edición de producto",
                date=datetime.datetime.now()
            )
            self.db.add(kardex_entry)

        product.name = name
        product.sku = sku
        product.price = price
        product.cost_price = cost_price
        product.stock = stock
        product.min_stock = min_stock
        product.is_box = is_box
        product.conversion_factor = conversion_factor
        product.unit_type = unit_type
        if category_id is not None:
            product.category_id = category_id
        if supplier_id is not None:
            product.supplier_id = supplier_id
        
        self.db.commit()
        return product

    def delete_product(self, product_id):
        """Logically delete a product (set is_active=False)"""
        product = self.db.query(Product).get(product_id)
        if not product:
            raise ValueError("Producto no encontrado")
        
        product.is_active = False
        self.db.commit()
        return True

    def get_active_products(self):
        """Get all active products"""
        return self.db.query(Product).filter(Product.is_active == True).all()

    def get_all_products(self):
        """Get all products (including inactive)"""
        return self.db.query(Product).all()

    def get_product_by_id(self, product_id):
        return self.db.query(Product).get(product_id)
