from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
from ..db.session import get_db
from ..services.change_addendum_service import ChangeAddendumService
from ..core.security import get_current_user
from ..models.user import User
from ..models.change_request_approval import ApprovalLevel, ApprovalStatus
from pydantic import BaseModel

router = APIRouter()

class ChangeAddendumRequest(BaseModel):
    original_request_id: int
    description: str
    impact_analysis: str
    technical_justification: str

class ApprovalUpdateRequest(BaseModel):
    status: ApprovalStatus
    comments: Optional[str] = None

@router.post("/change-addendum")
async def create_change_addendum(
    request: ChangeAddendumRequest,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new change addendum request with file attachments"""
    # TODO: Implement file storage service
    # For now, we'll use mock URLs
    file_urls = [f"https://storage.example.com/attachments/{file.filename}" for file in files]
    
    service = ChangeAddendumService(db)
    try:
        approval = await service.create_change_addendum(
            original_request_id=request.original_request_id,
            description=request.description,
            impact_analysis=request.impact_analysis,
            technical_justification=request.technical_justification,
            attachments=file_urls,
            user_id=current_user.id
        )
        return approval
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/change-addendum/{approval_id}/approve")
async def approve_change_addendum(
    approval_id: int,
    level: ApprovalLevel,
    approval: ApprovalUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update approval status for a change addendum"""
    service = ChangeAddendumService(db)
    try:
        result = await service.update_approval(
            approval_id=approval_id,
            level=level,
            status=approval.status,
            comments=approval.comments,
            user_id=current_user.id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
