from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class OrderBase(BaseModel):
    order_type: str
    priority: str = "normal"
    quantity: int
    remarks: Optional[str] = None
    required_date: Optional[datetime] = None
    
class OrderCreate(OrderBase):
    item_id: int
    warehouse_request_item_id: Optional[int] = None

class OrderUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    quantity: Optional[int] = None
    remarks: Optional[str] = None
    required_date: Optional[datetime] = None
    vendor_name: Optional[str] = None
    price: Optional[float] = None

class Order(OrderBase):
    id: int
    status: str
    created_by_id: int
    item_id: int
    warehouse_request_item_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    vendor_name: Optional[str] = None
    price: Optional[float] = None

    class Config:
        orm_mode = True
