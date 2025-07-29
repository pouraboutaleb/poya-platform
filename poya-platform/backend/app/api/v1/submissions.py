from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.schemas.general_submission import (
    Submission,
    SubmissionCreate,
    SubmissionUpdate,
    SubmissionList
)
from app.models.user import User
from app.services.submission_service import submission_service

router = APIRouter()

@router.post("/submissions", response_model=Submission)
def create_submission(
    *,
    db: Session = Depends(get_db),
    submission_in: SubmissionCreate,
    current_user: User = Depends(get_current_user)
) -> Submission:
    """
    Create new submission.
    """
    submission = submission_service.create_submission(
        db=db, obj_in=submission_in, creator_id=current_user.id
    )
    return submission

@router.get("/submissions", response_model=SubmissionList)
def list_submissions(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    creator_id: int = Query(None),
    current_user: User = Depends(get_current_user)
) -> SubmissionList:
    """
    Retrieve submissions.
    """
    submissions = submission_service.get_submissions(
        db=db, skip=skip, limit=limit, creator_id=creator_id
    )
    total = len(submissions)  # You might want to do a separate count query for better performance
    return SubmissionList(total=total, submissions=submissions)

@router.get("/submissions/{submission_id}", response_model=Submission)
def get_submission(
    *,
    db: Session = Depends(get_db),
    submission_id: int,
    current_user: User = Depends(get_current_user)
) -> Submission:
    """
    Get submission by ID.
    """
    submission = submission_service.get_submission(db=db, submission_id=submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    return submission

@router.put("/submissions/{submission_id}", response_model=Submission)
def update_submission(
    *,
    db: Session = Depends(get_db),
    submission_id: int,
    submission_in: SubmissionUpdate,
    current_user: User = Depends(get_current_user)
) -> Submission:
    """
    Update submission.
    """
    submission = submission_service.get_submission(db=db, submission_id=submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    # Only allow creator to update
    if submission.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    submission = submission_service.update_submission(
        db=db, db_obj=submission, obj_in=submission_in
    )
    return submission
