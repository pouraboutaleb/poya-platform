from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from app.models.general_submission import GeneralSubmission, ImportanceLevel
from app.models.task import Task
from app.schemas.general_submission import SubmissionCreate, SubmissionUpdate
from datetime import datetime

class SubmissionService:
    def create_submission(self, db: Session, *, obj_in: SubmissionCreate, creator_id: int) -> GeneralSubmission:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = GeneralSubmission(**obj_in_data, creator_id=creator_id)

        # Create a task if importance level is HIGH or MEDIUM
        if obj_in.importance_level in [ImportanceLevel.HIGH, ImportanceLevel.MEDIUM]:
            task = Task(
                title=f"{obj_in.type}: {obj_in.title}",
                description=obj_in.description,
                creator_id=creator_id,
                assignee_id=obj_in.assignee_id,
                priority=4 if obj_in.importance_level == ImportanceLevel.HIGH else 3,
                due_date=datetime.utcnow(),  # You might want to calculate this based on importance
                status="new"
            )
            db.add(task)
            db.flush()  # Get task ID
            db_obj.task_id = task.id

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_submissions(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        creator_id: Optional[int] = None
    ) -> List[GeneralSubmission]:
        query = db.query(GeneralSubmission)
        if creator_id:
            query = query.filter(GeneralSubmission.creator_id == creator_id)
        return query.offset(skip).limit(limit).all()

    def get_submission(self, db: Session, submission_id: int) -> Optional[GeneralSubmission]:
        return db.query(GeneralSubmission).filter(GeneralSubmission.id == submission_id).first()

    def update_submission(
        self, db: Session, *, db_obj: GeneralSubmission, obj_in: SubmissionUpdate
    ) -> GeneralSubmission:
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(exclude_unset=True)
        
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

submission_service = SubmissionService()
