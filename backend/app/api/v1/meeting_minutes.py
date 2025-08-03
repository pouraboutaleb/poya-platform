from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from ...db.session import get_db
from ...core.security import get_current_user
from ...models.user import User
from ...schemas.meeting_minutes import MeetingMinutesCreate, MeetingMinutes
from ...schemas.task import TaskCreate, Task
from ...services.meeting_service import MeetingService
from ...services.task_service import TaskService

router = APIRouter()

@router.post("/meetings/{meeting_id}/minutes", response_model=MeetingMinutes)
async def create_meeting_minutes(
    meeting_id: int,
    minutes: MeetingMinutesCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    meeting_service = MeetingService(db)
    task_service = TaskService(db)
    
    # Verify user is meeting organizer
    meeting = meeting_service.get_meeting(meeting_id)
    if not meeting or meeting.organizer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the meeting organizer can add minutes"
        )
    
    # Create minutes
    db_minutes = meeting_service.create_minutes(meeting_id, minutes)
    
    # Create associated tasks if any
    if minutes.tasks:
        for task_create in minutes.tasks:
            task = task_service.create_task(
                task_create,
                creator_id=current_user.id,
                meeting_minutes_id=db_minutes.id
            )
    
    return db_minutes

@router.put("/meetings/{meeting_id}/minutes", response_model=MeetingMinutes)
async def update_meeting_minutes(
    meeting_id: int,
    minutes: MeetingMinutesCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    meeting_service = MeetingService(db)
    
    # Verify user is meeting organizer
    meeting = meeting_service.get_meeting(meeting_id)
    if not meeting or meeting.organizer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the meeting organizer can update minutes"
        )
    
    return meeting_service.update_minutes(meeting_id, minutes)

@router.post("/meetings/{meeting_id}/minutes/attachments")
async def upload_attachment(
    meeting_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    meeting_service = MeetingService(db)
    
    # Verify user is meeting organizer
    meeting = meeting_service.get_meeting(meeting_id)
    if not meeting or meeting.organizer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the meeting organizer can upload attachments"
        )
    
    file_url = await meeting_service.upload_minutes_attachment(meeting_id, file)
    return {"file_url": file_url}

@router.post("/meetings/{meeting_id}/minutes/{minutes_id}/tasks", response_model=Task)
async def create_task_from_minutes(
    meeting_id: int,
    minutes_id: int,
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    meeting_service = MeetingService(db)
    task_service = TaskService(db)
    
    # Verify user is meeting organizer
    meeting = meeting_service.get_meeting(meeting_id)
    if not meeting or meeting.organizer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the meeting organizer can create tasks"
        )
    
    return task_service.create_task(
        task,
        creator_id=current_user.id,
        meeting_minutes_id=minutes_id
    )
