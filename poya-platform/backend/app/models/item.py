from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship

from ..db.session import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    item_code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey("item_categories.id"), nullable=False)
    
    # Relationships
    category = relationship("ItemCategory", back_populates="items")
    warehouse_request_items = relationship("WarehouseRequestItem", back_populates="item")
    orders = relationship("Order", back_populates="item")
