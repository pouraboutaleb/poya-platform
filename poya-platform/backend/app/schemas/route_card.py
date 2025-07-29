from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class MaterialRequirement(BaseModel):
    item_id: int
    quantity: float
    unit: str

class WorkStation(BaseModel):
    name: str
    description: Optional[str] = None
    estimated_hours: float
    is_subcontractor: bool = False

class RouteCardBase(BaseModel):
    materials: List[MaterialRequirement]
    workstations: List[WorkStation]
    estimated_time: float

class RouteCardCreate(RouteCardBase):
    order_id: int

class RouteCardUpdate(BaseModel):
    materials: Optional[List[MaterialRequirement]] = None
    workstations: Optional[List[WorkStation]] = None
    estimated_time: Optional[float] = None
    status: Optional[str] = None

class RouteCard(RouteCardBase):
    id: int
    order_id: int
    status: str
    created_by_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
