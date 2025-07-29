from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..services.material_preparation_service import MaterialPreparationService
from ..schemas.task import Task
from ..core.security import get_current_active_user
from ..models.user import User

router = APIRouter()

@router.get("/preparation-tasks", response_model=List[Task])
def get_preparation_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all active material preparation tasks."""
    return MaterialPreparationService.get_active_preparation_tasks(db)

@router.post("/preparation-tasks/{task_id}/complete", response_model=Task)
def mark_materials_prepared(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark materials as prepared and create pickup task."""
    try:
        return MaterialPreparationService.mark_materials_prepared(
            db=db,
            task_id=task_id,
            user_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
