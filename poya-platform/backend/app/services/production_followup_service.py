from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy.orm import Session
from ..models.route_card import RouteCard, RouteStatus
from ..models.task import Task, TaskStatus, TaskType

class FollowUpStatus(str, Enum):
    ON_SCHEDULE = "on_schedule"
    DELAYED = "delayed"
    READY_FOR_PICKUP = "ready_for_pickup"

class ProductionFollowUpService:
    def __init__(self, db: Session):
        self.db = db

    async def log_followup(
        self,
        task_id: int,
        status: FollowUpStatus,
        notes: Optional[str] = None,
        revised_completion_date: Optional[datetime] = None,
        user_id: int = None
    ):
        # Get the task and associated route card
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task or task.type != TaskType.FOLLOWUP_WITH_SUBCONTRACTOR:
            raise ValueError("Invalid follow-up task")

        route_card = task.route_card

        # Update task status
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        task.completed_by_id = user_id
        task.notes = notes

        # Add follow-up log to route card
        if not hasattr(route_card, 'followup_logs'):
            route_card.followup_logs = []
        
        log_entry = {
            "date": datetime.utcnow().isoformat(),
            "status": status,
            "notes": notes,
            "user_id": user_id,
            "revised_completion_date": revised_completion_date.isoformat() if revised_completion_date else None
        }
        route_card.followup_logs.append(log_entry)

        # Handle status-specific actions
        if status == FollowUpStatus.DELAYED:
            if not revised_completion_date:
                raise ValueError("Revised completion date is required when status is DELAYED")
            
            # Update route card with new date
            route_card.estimated_completion_date = revised_completion_date
            
            # TODO: Send notifications to managers (implement notification system)
            # self._notify_managers(route_card, revised_completion_date)
            
            # Create new follow-up task for the new date
            self._create_followup_task(route_card, revised_completion_date)
            
        elif status == FollowUpStatus.READY_FOR_PICKUP:
            # Create pickup task
            pickup_task = Task(
                type=TaskType.PICKUP_FROM_SUBCONTRACTOR,
                description=f"Pick up completed part from subcontractor for Route Card #{route_card.id}",
                route_card_id=route_card.id,
                due_date=datetime.utcnow(),  # Due immediately
                priority=1,  # High priority
                status=TaskStatus.PENDING
            )
            self.db.add(pickup_task)

        self.db.commit()
        return task

    def _create_followup_task(self, route_card: RouteCard, completion_date: datetime):
        """Create a new follow-up task based on the revised completion date"""
        task = Task(
            type=TaskType.FOLLOWUP_WITH_SUBCONTRACTOR,
            description=f"Follow up with subcontractor for Route Card #{route_card.id} (Rescheduled)",
            route_card_id=route_card.id,
            due_date=completion_date,
            priority=2,  # Medium priority
            status=TaskStatus.PENDING
        )
        self.db.add(task)
