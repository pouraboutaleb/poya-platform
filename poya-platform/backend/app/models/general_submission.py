from typing import Optional, List
from sqlalchemy import String, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base
import enum
from datetime import datetime

class SubmissionType(str, enum.Enum):
    REPORT = "REPORT"
    PROBLEM = "PROBLEM"
    SUGGESTION = "SUGGESTION"

class ImportanceLevel(str, enum.Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class GeneralSubmission(Base):
    __tablename__ = "general_submissions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    type: Mapped[SubmissionType] = mapped_column(SQLEnum(SubmissionType))
    description: Mapped[str] = mapped_column(String)
    importance_level: Mapped[ImportanceLevel] = mapped_column(SQLEnum(ImportanceLevel))
    
    # File attachments - Assuming you have a FileAttachment model
    attachments: Mapped[List["FileAttachment"]] = relationship(back_populates="submission")
    
    # Creator relationship
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    creator: Mapped["User"] = relationship(back_populates="submissions")
    
    # Related task (optional)
    task_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tasks.id"), nullable=True)
    task: Mapped[Optional["Task"]] = relationship()
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )
