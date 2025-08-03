from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..db.base_class import Base

class WarehouseRequestStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    AWAITING_APPROVAL = "awaiting_approval"
    CHANGES_APPROVED = "changes_approved"
    CHANGES_REJECTED = "changes_rejected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class WarehouseRequestItemStatus(str, enum.Enum):
    PENDING = "pending"
    READY = "ready"
    BACKORDERED = "backordered"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"

class WarehouseRequestType(str, enum.Enum):
    STANDARD = "standard"
    CHANGE_ADDENDUM = "change_addendum"
    SPECIAL_REQUEST = "special_request"

class WarehouseRequest(Base):
    __tablename__ = "warehouse_request"

    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String, nullable=False)
    description = Column(String)
    priority = Column(String, default="normal")  # low, normal, high, urgent
    status = Column(String, default=WarehouseRequestStatus.DRAFT)
    request_type = Column(Enum(WarehouseRequestType), default=WarehouseRequestType.STANDARD)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    requested_delivery_date = Column(DateTime(timezone=True))
    
    # Foreign Keys
    created_by_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    original_request_id = Column(Integer, ForeignKey("warehouse_request.id"), nullable=True)  # For change addendums
    
    # Relationships
    created_by = relationship("User", back_populates="warehouse_requests")
    request_items = relationship("WarehouseRequestItem", back_populates="request", cascade="all, delete-orphan")
    change_approvals = relationship("ChangeRequestApproval", back_populates="warehouse_request", cascade="all, delete-orphan")
    original_request = relationship("WarehouseRequest", remote_side=[id], backref="change_requests")

class WarehouseRequestItem(Base):
    __tablename__ = "warehouse_request_item"

    id = Column(Integer, primary_key=True, index=True)
    quantity_requested = Column(Integer, nullable=False)
    quantity_fulfilled = Column(Integer, default=0)
    status = Column(String, default=WarehouseRequestItemStatus.PENDING)
    remarks = Column(String)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Foreign Keys
    request_id = Column(Integer, ForeignKey("warehouse_request.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("item.id"), nullable=False)
    
    # Relationships
    request = relationship("WarehouseRequest", back_populates="request_items")
    item = relationship("Item", back_populates="warehouse_request_items")
    orders = relationship("Order", back_populates="warehouse_request_item")
