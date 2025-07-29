from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime, String
from sqlalchemy.orm import relationship

from ..db.session import Base

class ProductionLog(Base):
    __tablename__ = "production_logs"

    id = Column(Integer, primary_key=True, index=True)
    quantity_produced = Column(Float, nullable=False)
    target_quantity = Column(Float, nullable=False)
    efficiency = Column(Float)  # Can be calculated from quantity_produced / target_quantity
    remarks = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    report_id = Column(Integer, ForeignKey("production_reports.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    
    # Relationships
    report = relationship("ProductionReport", back_populates="production_logs")
    item = relationship("Item")
