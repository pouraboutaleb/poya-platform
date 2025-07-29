from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from ..db.session import get_db
from ..services.qc_inspection_service import QCInspectionService, QCDecision
from ..core.security import get_current_user
from ..models.user import User
from ..models.task import Task, TaskType
from ..schemas.task import TaskResponse
from pydantic import BaseModel

router = APIRouter()

class QCDecisionRequest(BaseModel):
    decision: QCDecision
    notes: Optional[str] = None

@router.get("/inspection-tasks", response_model=List[TaskResponse])
async def get_inspection_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all active QC inspection tasks"""
    tasks = db.query(Task).filter(
        Task.type == TaskType.QC_INSPECTION,
        Task.status != "completed"
    ).all()
    return tasks

@router.get("/route-cards/{route_card_id}/details")
async def get_route_card_details(
    route_card_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get detailed information about a route card for QC inspection"""
    service = QCInspectionService(db)
    try:
        return await service.get_route_card_details(route_card_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/inspection-tasks/{task_id}/decision", response_model=TaskResponse)
async def make_qc_decision(
    task_id: int,
    decision: QCDecisionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record a QC decision for a task"""
    service = QCInspectionService(db)
    try:
        task = await service.process_qc_decision(
            task_id=task_id,
            decision=decision.decision,
            notes=decision.notes,
            user_id=current_user.id
        )
        return task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
