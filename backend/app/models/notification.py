from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..db.base_class import Base

class Notification(Base):
    __tablename__ = "notification"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    type = Column(String, nullable=False)  # INFO, WARNING, TASK, etc.
    read = Column(Boolean, default=False)
    link = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", backref="notifications")
