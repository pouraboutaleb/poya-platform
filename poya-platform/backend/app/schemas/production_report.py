from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import List, Optional
from enum import Enum

class ShiftEnum(str, Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    NIGHT = "night"

class ProductionLogBase(BaseModel):
    item_id: int
    quantity_produced: float
    target_quantity: float
    remarks: Optional[str] = None

class ProductionLogCreate(ProductionLogBase):
    pass

class ProductionLogResponse(ProductionLogBase):
    id: int
    report_id: int
    efficiency: Optional[float]
    created_at: datetime
    item_name: str
    item_code: str

    class Config:
        orm_mode = True

class StoppageType(str, Enum):
    MAINTENANCE = "maintenance"
    BREAKDOWN = "breakdown"
    MATERIAL_SHORTAGE = "material_shortage"
    SETUP_CHANGEOVER = "setup_changeover"
    QUALITY_ISSUE = "quality_issue"
    OTHER = "other"

class StoppageBase(BaseModel):
    type: StoppageType
    reason: str
    duration: float
    action_taken: Optional[str] = None

class StoppageCreate(StoppageBase):
    pass

class StoppageResponse(StoppageBase):
    id: int
    report_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class ProductionReportBase(BaseModel):
    report_date: date
    shift: ShiftEnum
    daily_challenge: Optional[str] = None
    solutions_implemented: Optional[str] = None
    notes: Optional[str] = None

class ProductionReportCreate(ProductionReportBase):
    production_logs: List[ProductionLogCreate]
    stoppages: List[StoppageCreate]

class ProductionReportResponse(ProductionReportBase):
    id: int
    created_by_id: int
    created_at: datetime
    updated_at: datetime
    production_logs: List[ProductionLogResponse]
    stoppages: List[StoppageResponse]
    created_by_name: str

    class Config:
        orm_mode = True
