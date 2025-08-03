from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from .item import ItemBase

class WarehouseRequestItemBase(BaseModel):
    item_id: int
    quantity_requested: int
    remarks: Optional[str] = None

class WarehouseRequestItemCreate(WarehouseRequestItemBase):
    pass

class WarehouseRequestItemUpdate(BaseModel):
    quantity_fulfilled: Optional[int] = None
    status: Optional[str] = None
    remarks: Optional[str] = None

class WarehouseRequestItem(WarehouseRequestItemBase):
    id: int
    request_id: int
    quantity_fulfilled: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
    item: ItemBase

    class Config:
        orm_mode = True

class WarehouseRequestBase(BaseModel):
    project_name: str
    description: Optional[str] = None
    priority: Optional[str] = "normal"
    requested_delivery_date: Optional[datetime] = None

class WarehouseRequestCreate(WarehouseRequestBase):
    request_items: List[WarehouseRequestItemCreate]

class WarehouseRequestUpdate(BaseModel):
    project_name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    requested_delivery_date: Optional[datetime] = None

class WarehouseRequest(WarehouseRequestBase):
    id: int
    status: str
    created_by_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    request_items: List[WarehouseRequestItem]

    class Config:
        orm_mode = True
