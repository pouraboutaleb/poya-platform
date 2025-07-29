from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.schemas.meeting import Meeting, MeetingCreate, MeetingUpdate, MeetingList
from app.models.user import User
from app.services.meeting_service import meeting_service

router = APIRouter()

@router.post("/meetings", response_model=Meeting)
def create_meeting(
    *,
    db: Session = Depends(get_db),
    meeting_in: MeetingCreate,
    current_user: User = Depends(get_current_user)
) -> Meeting:
    """
    Create a new meeting.
    """
    if current_user.id not in meeting_in.attendee_ids:
        # Automatically add organizer as an attendee if not included
        meeting_in.attendee_ids.append(current_user.id)

    meeting = meeting_service.create_meeting(
        db=db,
        obj_in=meeting_in,
        organizer_id=current_user.id
    )
    return meeting

@router.get("/meetings", response_model=MeetingList)
def list_meetings(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    include_past: bool = Query(False, description="Include past meetings in the results"),
    current_user: User = Depends(get_current_user)
) -> MeetingList:
    """
    Retrieve meetings.
    Returns meetings where the current user is either the organizer or an attendee.
    """
    meetings = meeting_service.get_meetings(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        include_past=include_past
    )
    total = len(meetings)  # For better performance, you might want to do a separate count query
    return MeetingList(total=total, meetings=meetings)

@router.get("/meetings/{meeting_id}", response_model=Meeting)
def get_meeting(
    *,
    db: Session = Depends(get_db),
    meeting_id: int,
    current_user: User = Depends(get_current_user)
) -> Meeting:
    """
    Get meeting by ID.
    Only accessible by meeting organizer or attendees.
    """
    meeting = meeting_service.get_meeting(
        db=db,
        meeting_id=meeting_id,
        user_id=current_user.id
    )
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting

@router.put("/meetings/{meeting_id}", response_model=Meeting)
def update_meeting(
    *,
    db: Session = Depends(get_db),
    meeting_id: int,
    meeting_in: MeetingUpdate,
    current_user: User = Depends(get_current_user)
) -> Meeting:
    """
    Update meeting.
    Only the organizer can update the meeting.
    """
    meeting = meeting_service.get_meeting(
        db=db,
        meeting_id=meeting_id,
        user_id=current_user.id
    )
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    if meeting.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the meeting organizer can update the meeting")
    
    updated_meeting = meeting_service.update_meeting(
        db=db,
        db_obj=meeting,
        obj_in=meeting_in
    )
    return updated_meeting

@router.post("/meetings/{meeting_id}/cancel", response_model=Meeting)
def cancel_meeting(
    *,
    db: Session = Depends(get_db),
    meeting_id: int,
    current_user: User = Depends(get_current_user)
) -> Meeting:
    """
    Cancel a meeting.
    Only the organizer can cancel the meeting.
    """
    meeting = meeting_service.get_meeting(
        db=db,
        meeting_id=meeting_id,
        user_id=current_user.id
    )
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    if meeting.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the meeting organizer can cancel the meeting")

    if meeting.is_cancelled:
        raise HTTPException(status_code=400, detail="Meeting is already cancelled")

    cancelled_meeting = meeting_service.cancel_meeting(db=db, db_obj=meeting)
    return cancelled_meeting
