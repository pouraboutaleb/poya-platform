from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..db.base_class import Base

class OrderType(str, enum.Enum):
    PROCUREMENT = "procurement"
    PRODUCTION = "production"

class OrderStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Order(Base):
    __tablename__ = "order"

    id = Column(Integer, primary_key=True, index=True)
    order_type = Column(Enum(OrderType), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.DRAFT)
    priority = Column(String, default="normal")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    required_date = Column(DateTime(timezone=True))
    
    # Foreign Keys
    created_by_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("item.id"), nullable=False)
    warehouse_request_item_id = Column(Integer, ForeignKey("warehouse_request_item.id"), nullable=True)
    
    # Order details
    quantity = Column(Integer, nullable=False)
    remarks = Column(String)
    
    # Procurement details
    vendor_name = Column(String, nullable=True)
    price = Column(Integer, nullable=True)  # Store price in cents to avoid floating point issues
    
    # Relationships
    created_by = relationship("User", back_populates="orders")
    item = relationship("Item", back_populates="orders")
    warehouse_request_item = relationship("WarehouseRequestItem", back_populates="orders")
    tasks = relationship("Task", back_populates="order")
    route_card = relationship("RouteCard", back_populates="order", uselist=False)
