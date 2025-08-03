from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from enum import Enum

from ..db.base_class import Base

class ShiftEnum(str, Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    NIGHT = "night"

class ProductionReport(Base):
    __tablename__ = "production_report"

    id = Column(Integer, primary_key=True, index=True)
    report_date = Column(Date, nullable=False)
    shift = Column(SQLEnum(ShiftEnum), nullable=False)
    daily_challenge = Column(Text)
    solutions_implemented = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    created_by_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    
    # Relationships
    created_by = relationship("User", back_populates="production_reports")
    production_logs = relationship("ProductionLog", back_populates="report", cascade="all, delete-orphan")
    stoppages = relationship("Stoppage", back_populates="report", cascade="all, delete-orphan")
