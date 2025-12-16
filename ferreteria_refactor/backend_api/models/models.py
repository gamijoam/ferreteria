from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, Text, DateTime, Enum
from sqlalchemy.orm import relationship
from ..database.db import Base
import datetime
import enum

class MovementType(enum.Enum):
    PURCHASE = "PURCHASE"
    SALE = "SALE"
    ADJUSTMENT = "ADJUSTMENT"  # For shrinkage, discounts, damaged goods
    RETURN = "RETURN"
    ADJUSTMENT_IN = "ADJUSTMENT_IN"
    ADJUSTMENT_OUT = "ADJUSTMENT_OUT"

# ============================================================================
# MULTI-CURRENCY SYSTEM
# ============================================================================

class Currency(Base):
    """Catalog of available currencies (USD, VES, EUR, etc.)"""
    __tablename__ = "currencies"

    code = Column(String(3), primary_key=True, index=True)  # USD, VES, EUR
    name = Column(String, nullable=False)  # Dólar Estadounidense, Bolívar
    symbol = Column(String, nullable=False)  # $, Bs, €

    exchange_rates = relationship("ExchangeRate", back_populates="currency")

    def __repr__(self):
        return f"<Currency(code='{self.code}', name='{self.name}')>"

class ExchangeRate(Base):
    """Dynamic exchange rates for different purposes (BCV, Monitor, Internal, etc.)"""
    __tablename__ = "exchange_rates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # "BCV", "Monitor", "Mayorista"
    currency_code = Column(String(3), ForeignKey("currencies.code"), nullable=False)
    rate = Column(Float, nullable=False)  # Conversion rate to base currency (USD)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    currency = relationship("Currency", back_populates="exchange_rates")
    products = relationship("Product", back_populates="default_rate")
    price_rules = relationship("PriceRule", back_populates="exchange_rate")

    def __repr__(self):
        return f"<ExchangeRate(name='{self.name}', rate={self.rate}, currency='{self.currency_code}')>"

# ============================================================================
# EXISTING MODELS
# ============================================================================

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
    contact_person = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.now)

    products = relationship("Product", back_populates="supplier")
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")

    def __repr__(self):
        return f"<Supplier(name='{self.name}')>"

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    sku = Column(String, unique=True, index=True, nullable=True) # Barcode
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False, default=0.0)
    price_mayor_1 = Column(Float, default=0.0) # Wholesale Price 1
    price_mayor_2 = Column(Float, default=0.0) # Wholesale Price 2
    cost_price = Column(Float, default=0.0)  # NEW: Cost for profit margin calculation
    stock = Column(Float, default=0.0) # Base units
    min_stock = Column(Float, default=5.0) # Low stock alert threshold
    is_active = Column(Boolean, default=True) # Logical delete

    # Core Logic for Hardware Store
    is_box = Column(Boolean, default=False)
    location = Column(String, nullable=True) # Shelf/Department location
    conversion_factor = Column(Integer, default=1) # How many units in the box?
    unit_type = Column(String, default="Unidad") # Unidad, Metro, Kilo, Litro

    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    
    # Exchange Rate Support
    default_rate_id = Column(Integer, ForeignKey("exchange_rates.id"), nullable=True)

    category = relationship("Category", back_populates="products")
    category = relationship("Category", back_populates="products")
    supplier = relationship("Supplier", back_populates="products")
    default_rate = relationship("ExchangeRate", back_populates="products")
    price_rules = relationship("PriceRule", back_populates="product")

    def __repr__(self):
        return f"<Product(name='{self.name}', is_box={self.is_box}, factor={self.conversion_factor})>"

class Kardex(Base):
    __tablename__ = "kardex"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    date = Column(DateTime, default=datetime.datetime.now)
    movement_type = Column(Enum(MovementType), nullable=False)
    quantity = Column(Float, nullable=False) # Positive or Negative
    balance_after = Column(Float, nullable=False)
    description = Column(Text, nullable=True)

    product = relationship("Product")

    def __repr__(self):
        return f"<Kardex(product='{self.product_id}', type='{self.movement_type}', qty={self.quantity})>"

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.datetime.now)
    total_amount = Column(Float, nullable=False)
    payment_method = Column(String, default="Efectivo") # Efectivo, Tarjeta, Credito
    
    # Dual Currency Support
    currency = Column(String, default="USD") # USD or BS
    exchange_rate_used = Column(Float, default=1.0) # Rate at time of sale
    total_amount_bs = Column(Float, nullable=True) # Amount in Bs if applicable
    
    # Credit Sales
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    is_credit = Column(Boolean, default=False)
    paid = Column(Boolean, default=True) # False for credit sales
    
    # Sale Notes
    notes = Column(Text, nullable=True)  # Special observations or instructions

    details = relationship("SaleDetail", back_populates="sale")
    customer = relationship("Customer", back_populates="sales")
    payments = relationship("SalePayment", back_populates="sale", lazy="joined")

    def __repr__(self):
        return f"<Sale(id={self.id}, total={self.total_amount})>"

class SalePayment(Base):
    __tablename__ = "sale_payments"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD") # USD or Bs
    payment_method = Column(String, default="Efectivo") # Efectivo, Tarjeta, etc.
    exchange_rate = Column(Float, default=1.0) # Rate used for this specific payment

    sale = relationship("Sale", back_populates="payments")

class SaleDetail(Base):
    __tablename__ = "sale_details"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Float, nullable=False) # Units sold
    unit_price = Column(Float, nullable=False) # Price at moment of sale
    
    # Discount Support
    discount = Column(Float, default=0.0)  # Discount amount or percentage
    discount_type = Column(String, default="NONE")  # NONE, PERCENT, FIXED
    
    subtotal = Column(Float, nullable=False)
    is_box_sale = Column(Boolean, default=False) # Was it sold as a box?
    
    # Audit: Exchange rate used at time of sale
    exchange_rate_name = Column(String, nullable=True)
    exchange_rate_value = Column(Float, nullable=True)

    sale = relationship("Sale", back_populates="details")
    product = relationship("Product")

    def __repr__(self):
        return f"<SaleDetail(product='{self.product_id}', qty={self.quantity})>"

class CashSession(Base):
    __tablename__ = "cash_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    start_time = Column(DateTime, default=datetime.datetime.now)
    end_time = Column(DateTime, nullable=True)
    initial_cash = Column(Float, default=0.0)
    initial_cash_bs = Column(Float, default=0.0) # Initial amount in Bs
    final_cash_reported = Column(Float, nullable=True) # What user counted (USD)
    final_cash_reported_bs = Column(Float, nullable=True) # What user counted (Bs)
    final_cash_expected = Column(Float, nullable=True) # Calculated (USD)
    final_cash_expected_bs = Column(Float, nullable=True) # Calculated (Bs)
    difference = Column(Float, nullable=True) # USD difference
    difference_bs = Column(Float, nullable=True) # Bs difference
    status = Column(String, default="OPEN") # OPEN, CLOSED

    movements = relationship("CashMovement", back_populates="session")
    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self):
        return f"<CashSession(id={self.id}, status='{self.status}')>"

class CashMovement(Base):
    __tablename__ = "cash_movements"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("cash_sessions.id"), nullable=False)
    type = Column(String, nullable=False) # EXPENSE, WITHDRAWAL, DEPOSIT
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD") # USD or BS
    exchange_rate = Column(Float, default=1.0)
    description = Column(Text, nullable=True)
    date = Column(DateTime, default=datetime.datetime.now)

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
    pin = Column(String, nullable=True)  # 4-6 digit PIN for discount authorization
    role = Column(Enum(UserRole), default=UserRole.CASHIER)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role}')>"

class Return(Base):
    __tablename__ = "returns"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    date = Column(DateTime, default=datetime.datetime.now)
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
    quantity = Column(Float, nullable=False) # Units returned

    return_obj = relationship("Return", back_populates="details")
    product = relationship("Product")

    def __repr__(self):
        return f"<ReturnDetail(product='{self.product_id}', qty={self.quantity})>"

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    id_number = Column(String, nullable=True, index=True)  # Cédula/ID
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    credit_limit = Column(Float, default=0.0)

    sales = relationship("Sale", back_populates="customer")
    payments = relationship("Payment", back_populates="customer")

    def __repr__(self):
        return f"<Customer(name='{self.name}')>"

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(DateTime, default=datetime.datetime.now)
    description = Column(Text, nullable=True)
    
    # Dual Currency Support
    currency = Column(String, default="USD") # USD or BS
    exchange_rate_used = Column(Float, default=1.0) # Rate at time of payment
    amount_bs = Column(Float, nullable=True) # Amount in Bs if applicable
    payment_method = Column(String, default="Efectivo") # Efectivo, Transferencia, Tarjeta

    customer = relationship("Customer", back_populates="payments")

    def __repr__(self):
        return f"<Payment(customer={self.customer_id}, amount={self.amount})>"


class PriceRule(Base):
    __tablename__ = "price_rules"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    min_quantity = Column(Float, nullable=False)  # Minimum qty to apply this price
    price = Column(Float, nullable=False)  # Special price for this tier
    
    # Exchange Rate Support (allows different rates for wholesale)
    exchange_rate_id = Column(Integer, ForeignKey("exchange_rates.id"), nullable=True)

    product = relationship("Product", back_populates="price_rules")
    exchange_rate = relationship("ExchangeRate", back_populates="price_rules")

    def __repr__(self):
        return f"<PriceRule(product={self.product_id}, min_qty={self.min_quantity}, price={self.price})>"

class Quote(Base):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    date = Column(DateTime, default=datetime.datetime.now)
    total_amount = Column(Float, nullable=False)
    status = Column(String, default="PENDING")  # PENDING, CONVERTED, EXPIRED
    notes = Column(Text, nullable=True)

    customer = relationship("Customer")
    details = relationship("QuoteDetail", back_populates="quote")

    def __repr__(self):
        return f"<Quote(id={self.id}, total={self.total_amount}, status='{self.status}')>"

class QuoteDetail(Base):
    __tablename__ = "quote_details"

    id = Column(Integer, primary_key=True, index=True)
    quote_id = Column(Integer, ForeignKey("quotes.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    is_box_sale = Column(Boolean, default=False)

    quote = relationship("Quote", back_populates="details")
    product = relationship("Product")

    def __repr__(self):
        return f"<QuoteDetail(product={self.product_id}, qty={self.quantity})>"

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    order_date = Column(DateTime, default=datetime.datetime.now)
    expected_delivery = Column(DateTime, nullable=True)
    status = Column(String, default="PENDING")  # PENDING, RECEIVED, CANCELLED
    total_amount = Column(Float, default=0.0)
    notes = Column(Text, nullable=True)
    received_date = Column(DateTime, nullable=True)
    received_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    supplier = relationship("Supplier", back_populates="purchase_orders")
    details = relationship("PurchaseOrderDetail", back_populates="order")

    def __repr__(self):
        return f"<PurchaseOrder(id={self.id}, supplier={self.supplier_id}, status='{self.status}')>"

class PurchaseOrderDetail(Base):
    __tablename__ = "purchase_order_details"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    unit_cost = Column(Float, nullable=False)  # Cost per unit
    subtotal = Column(Float, nullable=False)

    order = relationship("PurchaseOrder", back_populates="details")
    product = relationship("Product")

    def __repr__(self):
        return f"<PurchaseOrderDetail(product={self.product_id}, qty={self.quantity}, cost={self.unit_cost})>"

class BusinessConfig(Base):
    __tablename__ = "business_config"

    key = Column(String, primary_key=True, index=True)
    value = Column(Text, nullable=True)
    
    # Dual Currency Support (stored as special keys)
    # exchange_rate: Current USD to Bs rate
    # exchange_rate_updated_at: Last update timestamp

    def __repr__(self):
        return f"<BusinessConfig(key='{self.key}', value='{self.value}')>"
