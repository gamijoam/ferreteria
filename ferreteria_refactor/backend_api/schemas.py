from pydantic import BaseModel
from typing import List, Optional

class ProductBase(BaseModel):
    name: str
    sku: Optional[str] = None
    price: float
    stock: float

class ProductRead(ProductBase):
    id: int
    is_box: bool
    conversion_factor: int
    
    class Config:
        from_attributes = True

class SaleDetailCreate(BaseModel):
    product_id: int
    quantity: float
    is_box: bool = False

class SaleCreate(BaseModel):
    customer_id: Optional[int] = None
    payment_method: str = "Efectivo"
    items: List[SaleDetailCreate]
    total_amount: float # Optionally passed from frontend or calculated backend
