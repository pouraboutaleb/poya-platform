from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db.session import Base

class MeetingMinutes(Base):
    __tablename__ = "meeting_minutes"

    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"))
    text_body = Column(String)
    attachments = Column(ARRAY(String))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    meeting = relationship("Meeting", back_populates="minutes")
    tasks = relationship("Task", back_populates="meeting_minutes")
