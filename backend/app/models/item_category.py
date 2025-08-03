from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from ..db.base_class import Base

class ItemCategory(Base):
    """Item category model"""
    __tablename__ = "item_category"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String, nullable=True)
    parent_id = Column(Integer, ForeignKey("item_category.id"), nullable=True)
    
    # Relationships
    parent = relationship("ItemCategory", remote_side=[id], back_populates="children")
    children = relationship("ItemCategory", back_populates="parent")
    items = relationship("Item", back_populates="category")

    def to_tree_dict(self):
        """Convert category to tree structure"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "children": [child.to_tree_dict() for child in self.children]
        }
