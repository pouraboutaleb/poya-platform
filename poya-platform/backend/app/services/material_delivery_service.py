from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from ..models.route_card import RouteCard, RouteLocation, RouteStatus
from ..models.task import Task, TaskStatus, TaskType
from ..schemas.task import TaskCreate

class MaterialDeliveryService:
    def __init__(self, db: Session):
        self.db = db

    async def confirm_delivery(
        self,
        task_id: int,
        estimated_completion_date: datetime,
        notes: Optional[str] = None,
        user_id: int = None
    ):
        # Get the task and associated route card
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task or task.type != TaskType.DELIVER_MATERIALS:
            raise ValueError("Invalid task")

        route_card = task.route_card

        # Update task status
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        task.completed_by_id = user_id
        task.notes = notes

        # Update route card status and location
        subcontractor_name = route_card.workstations[route_card.current_workstation_index].get('name', 'Unknown')
        route_card.current_location = RouteLocation.AT_SUBCONTRACTOR
        route_card.status = RouteStatus.IN_PRODUCTION

        # Create follow-up tasks
        self._create_followup_tasks(route_card, estimated_completion_date)

        self.db.commit()
        return task

    def _create_followup_tasks(self, route_card: RouteCard, estimated_completion_date: datetime):
        # Create a check-in task for halfway through the estimated time
        halfway_date = datetime.utcnow() + ((estimated_completion_date - datetime.utcnow()) / 2)
        
        checkin_task = TaskCreate(
            type=TaskType.FOLLOWUP_WITH_SUBCONTRACTOR,
            description=f"Check progress with subcontractor for Route Card #{route_card.id}",
            due_date=halfway_date,
            route_card_id=route_card.id,
            priority=2  # Medium priority
        )

        # Create a final check task near the estimated completion date
        final_check_date = estimated_completion_date - timedelta(days=1)  # One day before
        final_task = TaskCreate(
            type=TaskType.FOLLOWUP_WITH_SUBCONTRACTOR,
            description=f"Final check with subcontractor for Route Card #{route_card.id} - Due tomorrow",
            due_date=final_check_date,
            route_card_id=route_card.id,
            priority=1  # High priority
        )

        # Add tasks to database
        for task_data in [checkin_task, final_task]:
            task = Task(**task_data.dict())
            self.db.add(task)
