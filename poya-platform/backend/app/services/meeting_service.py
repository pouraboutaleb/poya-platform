from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from app.models.meeting import Meeting, MeetingAgendaItem
from app.models.user import User
from app.schemas.meeting import MeetingCreate, MeetingUpdate

class MeetingService:
    def create_meeting(
        self, 
        db: Session, 
        *, 
        obj_in: MeetingCreate,
        organizer_id: int
    ) -> Meeting:
        # Create meeting object
        meeting_data = obj_in.dict(exclude={'attendee_ids', 'agenda_items'})
        db_obj = Meeting(**meeting_data, organizer_id=organizer_id)
        
        # Add attendees
        attendees = db.query(User).filter(User.id.in_(obj_in.attendee_ids)).all()
        db_obj.attendees = attendees
        
        # Add agenda items
        for idx, item in enumerate(obj_in.agenda_items):
            agenda_item = MeetingAgendaItem(
                **item.dict(),
                order=idx,
                meeting=db_obj
            )
            db.add(agenda_item)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_meetings(
        self,
        db: Session,
        *,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        include_past: bool = False
    ) -> List[Meeting]:
        query = db.query(Meeting).filter(
            or_(
                Meeting.organizer_id == user_id,
                Meeting.attendees.any(id=user_id)
            )
        )

        if not include_past:
            query = query.filter(Meeting.end_time >= datetime.utcnow())

        query = query.filter(Meeting.is_cancelled == False)
        query = query.order_by(Meeting.start_time.asc())
        
        return query.offset(skip).limit(limit).all()

    def get_meeting(
        self,
        db: Session,
        meeting_id: int,
        user_id: int
    ) -> Optional[Meeting]:
        return db.query(Meeting).filter(
            Meeting.id == meeting_id,
            or_(
                Meeting.organizer_id == user_id,
                Meeting.attendees.any(id=user_id)
            )
        ).first()

    def update_meeting(
        self,
        db: Session,
        *,
        db_obj: Meeting,
        obj_in: MeetingUpdate
    ) -> Meeting:
        update_data = obj_in.dict(exclude_unset=True)
        
        # Handle attendee updates separately
        if 'attendee_ids' in update_data:
            attendee_ids = update_data.pop('attendee_ids')
            attendees = db.query(User).filter(User.id.in_(attendee_ids)).all()
            db_obj.attendees = attendees

        # Handle agenda items updates separately
        if 'agenda_items' in update_data:
            agenda_items = update_data.pop('agenda_items')
            # Remove existing agenda items
            for item in db_obj.agenda_items:
                db.delete(item)
            # Add new agenda items
            for idx, item in enumerate(agenda_items):
                agenda_item = MeetingAgendaItem(
                    **item.dict(),
                    order=idx,
                    meeting=db_obj
                )
                db.add(agenda_item)

        # Update other fields
        obj_data = jsonable_encoder(db_obj)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def cancel_meeting(
        self,
        db: Session,
        *,
        db_obj: Meeting,
    ) -> Meeting:
        db_obj.is_cancelled = True
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

meeting_service = MeetingService()
