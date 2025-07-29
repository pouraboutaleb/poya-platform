from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from ..db.session import get_db
from ..services.material_delivery_service import MaterialDeliveryService
from ..core.security import get_current_user
from ..models.user import User
from ..schemas.task import Task, TaskResponse
from ..models.task import TaskType

router = APIRouter()

@router.get("/delivery-tasks", response_model=List[TaskResponse])
async def get_delivery_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all active material delivery tasks"""
    tasks = db.query(Task).filter(
        Task.type == TaskType.DELIVER_MATERIALS,
        Task.status != "completed"
    ).all()
    return tasks

@router.post("/delivery-tasks/{task_id}/confirm", response_model=TaskResponse)
async def confirm_delivery(
    task_id: int,
    estimated_completion_date: datetime,
    notes: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Confirm delivery of materials to subcontractor"""
    service = MaterialDeliveryService(db)
    try:
        task = await service.confirm_delivery(
            task_id=task_id,
            estimated_completion_date=estimated_completion_date,
            notes=notes,
            user_id=current_user.id
        )
        return task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
