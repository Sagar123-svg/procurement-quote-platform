from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field


class SupplierCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: str | None = None
    phone: str | None = None
    rating: float = Field(default=3.0, ge=1, le=5)
    


class SupplierOut(SupplierCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    unit: str = "pcs"


class ProductOut(ProductCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class QuoteCreate(BaseModel):
    supplier_id: int
    product_id: int
    unit_price: float = Field(gt=0)
    lead_time_days: int = Field(ge=0)
    valid_until: date | None = None


class QuoteOut(QuoteCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    
class RankedQuote(BaseModel):
    rank: int
    supplier_id: int
    supplier_name: str
    unit_price: float
    lead_time_days: int
    rating: float
    score: float