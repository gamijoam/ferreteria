from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, Text, DateTime, Enum
from sqlalchemy.orm import relationship
from src.database.db import Base
import datetime
import enum

class MovementType(enum.Enum):
    PURCHASE = "PURCHASE"
    SALE = "SALE"
    RETURN = "RETURN"
    ADJUSTMENT_IN = "ADJUSTMENT_IN"
    ADJUSTMENT_OUT = "ADJUSTMENT_OUT"

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)

    products = relationship("Product", back_populates="category")

    def __repr__(self):
        return f"<Category(name='{self.name}')>"

class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    contact_info = Column(Text, nullable=True)

    products = relationship("Product", back_populates="supplier")

    def __repr__(self):
        return f"<Supplier(name='{self.name}')>"

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    sku = Column(String, unique=True, index=True, nullable=True) # Barcode
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False, default=0.0)
    stock = Column(Integer, default=0) # Base units

    # Core Logic for Hardware Store
    is_box = Column(Boolean, default=False)
    conversion_factor = Column(Integer, default=1) # How many units in the box?
    unit_type = Column(String, default="Unidad") # Unidad, Metro, Kilo, Litro

    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)

    category = relationship("Category", back_populates="products")
    supplier = relationship("Supplier", back_populates="products")

    def __repr__(self):
        return f"<Product(name='{self.name}', is_box={self.is_box}, factor={self.conversion_factor})>"

class Kardex(Base):
    __tablename__ = "kardex"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    movement_type = Column(Enum(MovementType), nullable=False)
    quantity = Column(Integer, nullable=False) # Positive or Negative
    balance_after = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)

    product = relationship("Product")

    def __repr__(self):
        return f"<Kardex(product='{self.product_id}', type='{self.movement_type}', qty={self.quantity})>"

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    total_amount = Column(Float, nullable=False)
    payment_method = Column(String, default="Efectivo") # Efectivo, Tarjeta, Credito
    
    # Credit Sales
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    is_credit = Column(Boolean, default=False)
    paid = Column(Boolean, default=True) # False for credit sales

    details = relationship("SaleDetail", back_populates="sale")
    customer = relationship("Customer", back_populates="sales")

    def __repr__(self):
        return f"<Sale(id={self.id}, total={self.total_amount})>"

class SaleDetail(Base):
    __tablename__ = "sale_details"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False) # Units sold
    unit_price = Column(Float, nullable=False) # Price at moment of sale
    subtotal = Column(Float, nullable=False)
    is_box_sale = Column(Boolean, default=False) # Was it sold as a box?

    sale = relationship("Sale", back_populates="details")
    product = relationship("Product")

    def __repr__(self):
        return f"<SaleDetail(product='{self.product_id}', qty={self.quantity})>"

class CashSession(Base):
    __tablename__ = "cash_sessions"

    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    initial_cash = Column(Float, default=0.0)
    final_cash_reported = Column(Float, nullable=True) # What user counted
    final_cash_expected = Column(Float, nullable=True) # Calculated
    difference = Column(Float, nullable=True)
    status = Column(String, default="OPEN") # OPEN, CLOSED

    movements = relationship("CashMovement", back_populates="session")

    def __repr__(self):
        return f"<CashSession(id={self.id}, status='{self.status}')>"

class CashMovement(Base):
    __tablename__ = "cash_movements"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("cash_sessions.id"), nullable=False)
    type = Column(String, nullable=False) # EXPENSE, WITHDRAWAL, DEPOSIT
    amount = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    date = Column(DateTime, default=datetime.datetime.utcnow)

    session = relationship("CashSession", back_populates="movements")

    def __repr__(self):
        return f"<CashMovement(type='{self.type}', amount={self.amount})>"

class UserRole(enum.Enum):
    ADMIN = "ADMIN"
    CASHIER = "CASHIER"
    WAREHOUSE = "WAREHOUSE"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.CASHIER)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role}')>"

class Return(Base):
    __tablename__ = "returns"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    total_refunded = Column(Float, nullable=False)
    reason = Column(Text, nullable=True)

    sale = relationship("Sale")
    details = relationship("ReturnDetail", back_populates="return_obj")

    def __repr__(self):
        return f"<Return(id={self.id}, sale={self.sale_id})>"

class ReturnDetail(Base):
    __tablename__ = "return_details"

    id = Column(Integer, primary_key=True, index=True)
    return_id = Column(Integer, ForeignKey("returns.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False) # Units returned

    return_obj = relationship("Return", back_populates="details")
    product = relationship("Product")

    def __repr__(self):
        return f"<ReturnDetail(product='{self.product_id}', qty={self.quantity})>"

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    phone = Column(String, nullable=True)
    address = Column(Text, nullable=True)

    sales = relationship("Sale", back_populates="customer")
    payments = relationship("Payment", back_populates="customer")

    def __repr__(self):
        return f"<Customer(name='{self.name}')>"

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    description = Column(Text, nullable=True)

    customer = relationship("Customer", back_populates="payments")

    def __repr__(self):
        return f"<Payment(customer={self.customer_id}, amount={self.amount})>"
