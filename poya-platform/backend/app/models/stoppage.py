from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from ..db.session import Base

class StoppageType(str, enum):
    MAINTENANCE = "maintenance"
    BREAKDOWN = "breakdown"
    MATERIAL_SHORTAGE = "material_shortage"
    SETUP_CHANGEOVER = "setup_changeover"
    QUALITY_ISSUE = "quality_issue"
    OTHER = "other"

class Stoppage(Base):
    __tablename__ = "stoppages"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(SQLEnum(StoppageType), nullable=False)
    reason = Column(String, nullable=False)
    duration = Column(Float, nullable=False)  # Duration in minutes
    action_taken = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    report_id = Column(Integer, ForeignKey("production_reports.id"), nullable=False)
    
    # Relationships
    report = relationship("ProductionReport", back_populates="stoppages")
