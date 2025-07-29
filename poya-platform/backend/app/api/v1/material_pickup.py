from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..services.material_pickup_service import MaterialPickupService
from ..schemas.task import Task
from ..core.security import get_current_active_user
from ..models.user import User

router = APIRouter()

@router.get("/pickup-tasks", response_model=List[Task])
def get_pickup_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all active material pickup tasks."""
    return MaterialPickupService.get_active_pickup_tasks(db)

@router.post("/pickup-tasks/{task_id}/confirm", response_model=Task)
def confirm_pickup(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Confirm material pickup and create delivery task."""
    try:
        return MaterialPickupService.confirm_pickup(
            db=db,
            task_id=task_id,
            user_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
