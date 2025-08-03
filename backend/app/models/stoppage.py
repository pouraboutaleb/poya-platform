from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from enum import Enum

from ..db.base_class import Base

class StoppageType(str, Enum):
    MAINTENANCE = "maintenance"
    BREAKDOWN = "breakdown"
    MATERIAL_SHORTAGE = "material_shortage"
    SETUP_CHANGEOVER = "setup_changeover"
    QUALITY_ISSUE = "quality_issue"
    OTHER = "other"

class Stoppage(Base):
    __tablename__ = "stoppage"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(SQLEnum(StoppageType), nullable=False)
    reason = Column(String, nullable=False)
    duration = Column(Float, nullable=False)  # Duration in minutes
    action_taken = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    report_id = Column(Integer, ForeignKey("production_report.id"), nullable=False)
    
    # Relationships
    report = relationship("ProductionReport", back_populates="stoppages")
