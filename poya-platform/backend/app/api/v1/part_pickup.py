from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from ..db.session import get_db
from ..services.part_pickup_service import PartPickupService
from ..core.security import get_current_user
from ..models.user import User
from ..models.task import Task, TaskType
from ..schemas.task import TaskResponse
from pydantic import BaseModel

router = APIRouter()

class PickupConfirmation(BaseModel):
    quantity_received: int
    invoice_url: str
    notes: Optional[str] = None

@router.get("/pickup-tasks", response_model=List[TaskResponse])
async def get_pickup_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all active pickup tasks"""
    tasks = db.query(Task).filter(
        Task.type == TaskType.PICKUP_FROM_SUBCONTRACTOR,
        Task.status != "completed"
    ).all()
    return tasks

@router.post("/pickup-tasks/{task_id}/confirm", response_model=TaskResponse)
async def confirm_pickup(
    task_id: int,
    confirmation: PickupConfirmation,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Confirm pickup of completed part from subcontractor"""
    service = PartPickupService(db)
    try:
        task = await service.confirm_pickup(
            task_id=task_id,
            quantity_received=confirmation.quantity_received,
            invoice_url=confirmation.invoice_url,
            notes=confirmation.notes,
            user_id=current_user.id
        )
        return task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/pickup-tasks/upload-invoice")
async def upload_invoice(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload a service invoice"""
    try:
        # TODO: Implement file storage service
        # For now, we'll return a mock URL
        return {"invoice_url": f"https://storage.example.com/invoices/{file.filename}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
