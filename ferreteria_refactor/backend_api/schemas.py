from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

# Item Condition Enum for Returns
class ItemCondition(str, Enum):
    GOOD = "GOOD"
    DAMAGED = "DAMAGED"

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

# Sale Payment Schema
class SalePaymentCreate(BaseModel):
    sale_id: int
    amount: float
    currency: str = "USD"
    payment_method: str = "Efectivo"
    exchange_rate: float = 1.0

class SalePaymentRead(BaseModel):
    id: int
    amount: float
    currency: str
    payment_method: str
    exchange_rate: float
    
    class Config:
        from_attributes = True

class SaleRead(BaseModel):
    id: int
    date: datetime
    total_amount: float
    payment_method: str
    customer_id: Optional[int]
    customer: Optional['CustomerRead'] = None
    payments: List[SalePaymentRead] = []  # ✅ Include payments
    due_date: Optional[datetime] = None
    balance_pending: Optional[float] = None
    is_credit: bool = False  # ✅ CRITICAL: Missing field added
    paid: bool = True  # ✅ CRITICAL: Missing field added
    
    class Config:
        from_attributes = True

class CustomerBase(BaseModel):
    name: str
    id_number: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    credit_limit: float = 0.0
    payment_term_days: int = 15
    is_blocked: bool = False

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

# Cash Session Schemas
class CashSessionCurrencyCreate(BaseModel):
    currency_symbol: str
    initial_amount: float

class CashSessionCurrencyRead(BaseModel):
    id: int
    currency_symbol: str
    initial_amount: float
    final_reported: Optional[float] = None
    final_expected: Optional[float] = None
    difference: Optional[float] = None
    
    class Config:
        from_attributes = True

class CashSessionCreate(BaseModel):
    initial_cash: float = 0.0
    initial_cash_bs: float = 0.0
    currencies: List[CashSessionCurrencyCreate] = []

class CashSessionClose(BaseModel):
    final_cash_reported: float
    final_cash_reported_bs: float
    currencies: List[Dict] = []  # [{"symbol": "USD", "amount": 100}, ...]

class CashSessionRead(BaseModel):
    id: int
    start_time: datetime
    end_time: Optional[datetime]
    initial_cash: float
    initial_cash_bs: float
    final_cash_reported: Optional[float]
    final_cash_reported_bs: Optional[float]
    final_cash_expected: Optional[float]
    status: str
    movements: List[CashMovementRead] = []
    currencies: List[CashSessionCurrencyRead] = []

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
    # New: per-currency breakdown
    cash_by_currency: Optional[Dict[str, float]] = {}
    transfers_by_currency: Optional[Dict[str, Dict[str, float]]] = {}  # {currency: {method: amount}}

class CashSessionCloseResponse(BaseModel):
    session: CashSessionRead
    details: CashCloseDetails
    expected_usd: float
    expected_bs: float
    diff_usd: float
    diff_bs: float
    # New: per-currency expected/diff
    expected_by_currency: Optional[Dict[str, float]] = {}
    diff_by_currency: Optional[Dict[str, float]] = {}

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
    quantity: float
    condition: ItemCondition = ItemCondition.GOOD  # Default to GOOD condition
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

# Category Schemas
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None

class CategoryResponse(CategoryBase):
    id: int
    
    class Config:
        from_attributes = True

# Supplier Schemas

class SupplierBase(BaseModel):
    name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    payment_terms: Optional[int] = 30
    credit_limit: Optional[float] = None

class SupplierCreate(SupplierBase):
    pass

class SupplierRead(SupplierBase):
    id: int
    is_active: bool
    created_at: datetime
    current_balance: float = 0.0
    
    class Config:
        from_attributes = True

# Purchase Order and Payment Schemas

class PurchaseOrderBase(BaseModel):
    supplier_id: int
    invoice_number: Optional[str] = None
    notes: Optional[str] = None

class PurchaseItemCreate(BaseModel):
    product_id: int
    quantity: float
    unit_cost: float
    update_cost: bool = False

class PurchaseOrderCreate(PurchaseOrderBase):
    total_amount: float
    items: List[PurchaseItemCreate] = []
    payment_type: str = "CREDIT"  # CASH or CREDIT

class PurchaseOrderUpdate(BaseModel):
    invoice_number: Optional[str] = None
    notes: Optional[str] = None

class PurchaseOrderResponse(PurchaseOrderBase):
    id: int
    purchase_date: datetime
    due_date: Optional[datetime] = None
    total_amount: float
    paid_amount: float
    payment_status: str
    supplier: Optional['SupplierRead'] = None  # Include supplier details
    
    class Config:
        from_attributes = True

class PurchasePaymentCreate(BaseModel):
    amount: float
    payment_method: str = "Efectivo"
    reference: Optional[str] = None
    notes: Optional[str] = None

class PurchasePaymentResponse(BaseModel):
    id: int
    purchase_id: int
    amount: float
    payment_date: datetime
    payment_method: str
    reference: Optional[str] = None
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True

class SupplierStatsResponse(BaseModel):
    supplier_id: int
    supplier_name: str
    current_balance: float
    credit_limit: Optional[float] = None
    pending_purchases: int
    total_purchases: int
    
    class Config:
        from_attributes = True
