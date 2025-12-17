from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ProductBase(BaseModel):
    name: str
    sku: Optional[str] = None
    price: float
    price_mayor_1: Optional[float] = 0.0
    price_mayor_2: Optional[float] = 0.0
    stock: float
    description: Optional[str] = None
    cost_price: Optional[float] = 0.0
    min_stock: Optional[float] = 5.0
    unit_type: Optional[str] = "Unidad" # Added to match model
    is_box: bool = False
    conversion_factor: int = 1
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None
    location: Optional[str] = None

class ProductUnitBase(BaseModel):
    unit_name: str
    conversion_factor: float
    barcode: Optional[str] = None
    price_usd: Optional[float] = None
    is_default: bool = False

class ProductUnitCreate(ProductUnitBase):
    pass

class ProductUnitRead(ProductUnitBase):
    id: int
    product_id: int

    class Config:
        from_attributes = True

class ProductCreate(ProductBase):
    units: List[ProductUnitCreate] = []

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    sku: Optional[str] = None
    price: Optional[float] = None
    price_mayor_1: Optional[float] = None
    price_mayor_2: Optional[float] = None
    stock: Optional[float] = None
    description: Optional[str] = None
    cost_price: Optional[float] = None
    min_stock: Optional[float] = None
    is_box: Optional[bool] = None
    conversion_factor: Optional[int] = None
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None
    location: Optional[str] = None
    unit_type: Optional[str] = None
    is_active: Optional[bool] = None
    units: Optional[List[ProductUnitCreate]] = None

    class Config:
        from_attributes = True

class PriceRuleCreate(BaseModel):
    product_id: int
    min_quantity: float
    price: float

class PriceRuleRead(BaseModel):
    id: int
    product_id: int
    min_quantity: float
    price: float

    class Config:
        from_attributes = True

class ProductRead(ProductBase):
    id: int
    price_rules: List[PriceRuleRead] = []
    units: List[ProductUnitRead] = []
    
    class Config:
        from_attributes = True

class SaleDetailCreate(BaseModel):
    product_id: int
    quantity: float  # Quantity of THIS unit (e.g., 2 Kilos, 3 Sacos)
    unit_price_usd: float  # Price per unit sold (e.g., $4 per Kilo)
    conversion_factor: float = 1.0  # How many base units this represents (e.g., 1 Kilo = 1kg base)
    discount: float = 0.0
    discount_type: str = "NONE"  # NONE, PERCENT, FIXED

class SalePaymentCreate(BaseModel):
    amount: float
    currency: str
    payment_method: str
    exchange_rate: float = 1.0

class SaleCreate(BaseModel):
    customer_id: Optional[int] = None
    payment_method: str = "Efectivo" # Main method (for legacy/display)
    payments: List[SalePaymentCreate] = [] # List of specific payments
    items: List[SaleDetailCreate]
    total_amount: float
    currency: str = "USD"
    exchange_rate: float = 1.0
    notes: Optional[str] = None
    is_credit: bool = False

class SaleRead(BaseModel):
    id: int
    date: datetime
    total_amount: float
    payment_method: str
    customer_id: Optional[int]
    customer: Optional['CustomerRead'] = None
    
    class Config:
        from_attributes = True

class CustomerBase(BaseModel):
    name: str
    id_number: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerPaymentCreate(BaseModel):
    amount: float
    description: Optional[str] = None
    payment_method: str = "Efectivo"
    currency: str = "USD"
    exchange_rate: float = 1.0

class StockAdjustmentCreate(BaseModel):
    product_id: int
    quantity: float
    is_box_input: bool = False
    description: str = "Ajuste de Salida"
    movement_type: str = "ADJUSTMENT_OUT" # PURCHASE, ADJUSTMENT_OUT

class KardexRead(BaseModel):
    id: int
    product_id: int
    date: datetime
    movement_type: str
    quantity: float
    balance_after: float
    description: Optional[str]
    product: Optional[ProductRead] = None

    class Config:
        from_attributes = True

class CustomerRead(CustomerBase):
    id: int
    
    class Config:
        from_attributes = True

class QuoteDetailCreate(BaseModel):
    product_id: int
    quantity: float
    is_box: bool = False
    unit_price: float 
    subtotal: float

class QuoteCreate(BaseModel):
    customer_id: Optional[int] = None
    items: List[QuoteDetailCreate]
    total_amount: float
    notes: Optional[str] = None

class QuoteDetailRead(BaseModel):
    id: int
    product_id: int
    quantity: float
    unit_price: float
    subtotal: float
    is_box_sale: bool
    product: Optional[ProductRead] = None # Include product info for display

    class Config:
        from_attributes = True

class QuoteRead(BaseModel):
    id: int
    date: datetime
    customer_id: Optional[int]
    total_amount: float
    status: str = "PENDING"
    notes: Optional[str]
    customer: Optional[CustomerRead] = None

    class Config:
        from_attributes = True

class QuoteReadWithDetails(QuoteRead):
    details: List[QuoteDetailRead]
    notes: Optional[str]
    customer: Optional[CustomerRead] = None

    class Config:
        from_attributes = True


class CashMovementCreate(BaseModel):
    amount: float
    type: str # IN, OUT
    currency: str = "USD"
    description: str
    session_id: Optional[int] = None

class CashMovementRead(CashMovementCreate):
    id: int
    date: datetime
    
    class Config:
        from_attributes = True

class CashSessionCreate(BaseModel):
    initial_cash: float
    initial_cash_bs: float = 0.0

class CashSessionClose(BaseModel):
    final_cash_reported: float
    final_cash_reported_bs: float

class CashSessionRead(BaseModel):
    id: int
    start_time: datetime
    end_time: Optional[datetime]
    initial_cash: float
    initial_cash_bs: float
    final_cash_reported: Optional[float]
    final_cash_expected: Optional[float]
    status: str
    movements: List[CashMovementRead] = []

    class Config:
        from_attributes = True

class CashCloseDetails(BaseModel):
    initial_usd: float
    initial_bs: float
    sales_total: float
    sales_by_method: dict
    expenses_usd: float
    expenses_bs: float
    deposits_usd: float
    deposits_bs: float

class CashSessionCloseResponse(BaseModel):
    session: CashSessionRead
    details: CashCloseDetails
    expected_usd: float
    expected_bs: float
    diff_usd: float
    diff_bs: float

class SupplierBase(BaseModel):
    name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    is_active: bool = True

class SupplierCreate(SupplierBase):
    pass

class SupplierRead(SupplierBase):
    id: int

    class Config:
        from_attributes = True

class ReturnItemCreate(BaseModel):
    product_id: int
    product: Optional[ProductRead] = None

    class Config:
        from_attributes = True

class ReturnCreate(BaseModel):
    sale_id: int # Often implicit in URL but good to have
    items: List[ReturnItemCreate]
    reason: Optional[str] = None
    refund_currency: str = "USD"
    exchange_rate: float = 1.0

class ReturnDetailRead(BaseModel):
    id: int
    product_id: int
    quantity: float
    unit_price: float
    product: Optional[ProductRead] = None

    class Config:
        from_attributes = True

class ReturnRead(BaseModel):
    id: int
    sale_id: int
    date: datetime
    total_refunded: float
    reason: Optional[str]
    details: List[ReturnDetailRead] = []

    class Config:
        from_attributes = True

class PurchaseOrderItemCreate(BaseModel):
    product_id: int
    quantity: float
    unit_cost: float

class PurchaseOrderCreate(BaseModel):
    supplier_id: int
    items: List[PurchaseOrderItemCreate]
    expected_delivery: Optional[datetime] = None
    notes: Optional[str] = None

class PurchaseOrderDetailRead(BaseModel):
    id: int
    product_id: int
    quantity: float
    unit_cost: float
    subtotal: float
    product: Optional[ProductRead] = None

    class Config:
        from_attributes = True

class PurchaseOrderRead(BaseModel):
    id: int
    supplier_id: int
    order_date: datetime
    total_amount: float
    status: str
    expected_delivery: Optional[datetime]
    received_date: Optional[datetime]
    received_by: Optional[int]
    notes: Optional[str]
    details: List[PurchaseOrderDetailRead] = []
    supplier: Optional[SupplierRead] = None

    class Config:
        from_attributes = True

class PurchaseOrderReceive(BaseModel):
    user_id: int = 1  # Default user

# User Management Schemas
class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "CASHIER"  # ADMIN, CASHIER, MANAGER
    full_name: Optional[str] = None

class UserUpdate(BaseModel):
    password: Optional[str] = None
    role: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None

class UserRead(BaseModel):
    id: int
    username: str
    role: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

# Business Configuration Schemas
class BusinessConfigBase(BaseModel):
    key: str
    value: Optional[str] = None

class BusinessConfigRead(BusinessConfigBase):
    pass

class BusinessConfigCreate(BusinessConfigBase):
    pass

class BulkImportResult(BaseModel):
    success_count: int
    failed_count: int
    errors: List[str]

# Currency Schemas
class CurrencyBase(BaseModel):
    name: str
    symbol: str
    rate: float
    is_anchor: bool = False
    is_active: bool = True

class CurrencyCreate(CurrencyBase):
    pass

class CurrencyUpdate(BaseModel):
    name: Optional[str] = None
    symbol: Optional[str] = None
    rate: Optional[float] = None
    is_anchor: Optional[bool] = None
    is_active: Optional[bool] = None

class CurrencyRead(CurrencyBase):
    id: int

    class Config:
        from_attributes = True

# Inventory/Kardex Schemas
class StockAdjustmentCreate(BaseModel):
    product_id: int
    type: str  # ADJUSTMENT_IN, ADJUSTMENT_OUT, DAMAGED, INTERNAL_USE
    quantity: float  # Already in base units
    reason: str

class KardexRead(BaseModel):
    id: int
    product_id: int
    date: datetime
    movement_type: str
    quantity: float
    balance_after: float
    description: Optional[str] = None
    product: Optional['ProductRead'] = None
    
    class Config:
        from_attributes = True
