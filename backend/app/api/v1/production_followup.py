from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ...db.session import get_db
from ...services.production_followup_service import ProductionFollowUpService, FollowUpStatus
from ...core.security import get_current_user
from ...models.user import User
from ...models.task import TaskType, Task
from ...schemas.task import TaskResponse
from pydantic import BaseModel

router = APIRouter()

class FollowUpUpdate(BaseModel):
    status: FollowUpStatus
    notes: Optional[str] = None
    revised_completion_date: Optional[datetime] = None

@router.get("/followup-tasks", response_model=List[TaskResponse])
async def get_followup_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all active follow-up tasks"""
    tasks = db.query(Task).filter(
        Task.type == TaskType.FOLLOWUP_WITH_SUBCONTRACTOR,
        Task.status != "completed"
    ).all()
    return tasks

@router.post("/followup-tasks/{task_id}", response_model=TaskResponse)
async def log_followup(
    task_id: int,
    update: FollowUpUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Log a follow-up with the subcontractor"""
    service = ProductionFollowUpService(db)
    try:
        task = await service.log_followup(
            task_id=task_id,
            status=update.status,
            notes=update.notes,
            revised_completion_date=update.revised_completion_date,
            user_id=current_user.id
        )
        return task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
