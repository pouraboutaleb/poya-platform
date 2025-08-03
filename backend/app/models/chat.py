from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..db.base_class import Base

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    group_id = Column(Integer, ForeignKey("chat_groups.id"), nullable=True)
    content = Column(String, nullable=False)
    read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    sender = relationship("User", foreign_keys=[sender_id], backref="sent_messages")
    receiver = relationship("User", foreign_keys=[receiver_id], backref="received_messages")
    group = relationship("ChatGroup", back_populates="messages")

class ChatGroup(Base):
    __tablename__ = "chat_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_by_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    created_by = relationship("User", backref="created_chat_groups")
    members = relationship("User", secondary="chat_group_members", backref="chat_groups")
    messages = relationship("ChatMessage", back_populates="group")
