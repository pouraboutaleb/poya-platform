from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from typing import List
from ..db.base_class import Base

class RouteLocation(str, enum.Enum):
    WAREHOUSE = "warehouse"
    WITH_EXPEDITER = "with_expediter"
    AT_WORKSTATION = "at_workstation"
    AT_SUBCONTRACTOR = "at_subcontractor"
    QC_AREA = "qc_area"
    COMPLETED = "completed"

class RouteStatus(str, enum.Enum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    MATERIALS_PREPARED = "materials_prepared"
    MATERIALS_IN_TRANSIT = "materials_in_transit"
    IN_PRODUCTION = "in_production"
    AWAITING_QC = "awaiting_qc"
    NEEDS_REWORK = "needs_rework"
    AWAITING_SCRAP_APPROVAL = "awaiting_scrap_approval"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class RouteCard(Base):
    __tablename__ = "route_card"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("order.id"), nullable=False)
    status = Column(Enum(RouteStatus), default=RouteStatus.DRAFT)
    current_location = Column(Enum(RouteLocation), default=RouteLocation.WAREHOUSE)
    current_workstation_index = Column(Integer, default=0)  # Index in the workstations array
    
    # Route information
    materials = Column(JSON, nullable=False)  # List of required materials with quantities
    workstations = Column(JSON, nullable=False)  # Sequence of workstations/subcontractors
    estimated_time = Column(Float)  # Estimated production time in hours
    
    # Metadata
    created_by_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    order = relationship("Order", back_populates="route_card")
    created_by = relationship("User")
    tasks = relationship("Task", back_populates="route_card")
