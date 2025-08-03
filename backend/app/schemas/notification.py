"""Notification schema definitions"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum


class NotificationType(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"


class NotificationBase(BaseModel):
    title: str
    message: str
    type: NotificationType = NotificationType.INFO


class NotificationCreate(NotificationBase):
    user_id: int


class NotificationResponse(NotificationBase):
    id: int
    user_id: int
    is_read: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
