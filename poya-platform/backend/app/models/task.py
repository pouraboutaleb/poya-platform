from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime

from .user import Base

class TaskStatus(str, enum.Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    PENDING_REVIEW = "pending_review"
    NEEDS_REVISION = "needs_revision"
    COMPLETED = "completed"
    CANCELED = "canceled"

class TaskType(str, enum.Enum):
    MATERIAL_PREPARATION = "material_preparation"
    MATERIAL_PICKUP = "material_pickup"
    PRODUCTION = "production"
    QUALITY_CHECK = "quality_check"
    PROCUREMENT = "procurement"
    OTHER = "other"

class TaskPriority(int, enum.Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.NEW, nullable=False)
    priority = Column(SQLEnum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    due_date = Column(DateTime(timezone=True))
    
    # Foreign Keys
    assignee_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    
    # Relationships
    assignee = relationship("User", foreign_keys=[assignee_id], back_populates="assigned_tasks")
    creator = relationship("User", foreign_keys=[creator_id], back_populates="created_tasks")

    def __repr__(self):
        return f"<Task {self.id}: {self.title} ({self.status})>"
