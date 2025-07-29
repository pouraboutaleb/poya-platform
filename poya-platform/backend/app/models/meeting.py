from typing import Optional, List
from sqlalchemy import String, DateTime, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base
from datetime import datetime

# Association table for meeting attendees
meeting_attendees = Table(
    "meeting_attendees",
    Base.metadata,
    Column("meeting_id", ForeignKey("meetings.id"), primary_key=True),
    Column("user_id", ForeignKey("users.id"), primary_key=True)
)

class Meeting(Base):
    __tablename__ = "meetings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    purpose: Mapped[str] = mapped_column(String)
    start_time: Mapped[datetime] = mapped_column(DateTime)
    end_time: Mapped[datetime] = mapped_column(DateTime)
    location: Mapped[str] = mapped_column(String(255))

    # Organizer
    organizer_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    organizer: Mapped["User"] = relationship(foreign_keys=[organizer_id])

    # Attendees (many-to-many relationship)
    attendees: Mapped[List["User"]] = relationship(
        secondary=meeting_attendees,
        backref="meetings_attending"
    )

    # Agenda items (one-to-many relationship)
    agenda_items: Mapped[List["MeetingAgendaItem"]] = relationship(
        back_populates="meeting",
        cascade="all, delete-orphan"
    )

    # Minutes (one-to-one relationship)
    minutes: Mapped[Optional["MeetingMinutes"]] = relationship(
        back_populates="meeting",
        uselist=False,
        cascade="all, delete-orphan"
    )

    # Status tracking
    is_cancelled: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

class MeetingAgendaItem(Base):
    __tablename__ = "meeting_agenda_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.id"))
    topic: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    duration_minutes: Mapped[int] = mapped_column(default=15)
    order: Mapped[int] = mapped_column(default=0)

    # Presenter
    presenter_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    presenter: Mapped[Optional["User"]] = relationship()

    # Back reference to meeting
    meeting: Mapped["Meeting"] = relationship(back_populates="agenda_items")

class MeetingMinutes(Base):
    __tablename__ = "meeting_minutes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.id"), unique=True)
    text_body: Mapped[str] = mapped_column(String)
    
    # File attachments - Assuming you have a FileAttachment model
    attachments: Mapped[List["FileAttachment"]] = relationship(
        back_populates="meeting_minutes"
    )

    # Back reference to meeting
    meeting: Mapped["Meeting"] = relationship(back_populates="minutes")

    # Creation tracking
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_by: Mapped["User"] = relationship()
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
