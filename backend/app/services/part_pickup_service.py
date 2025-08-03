from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from ..models.route_card import RouteCard, RouteLocation, RouteStatus
from ..models.task import Task, TaskStatus, TaskType

class PartPickupService:
    def __init__(self, db: Session):
        self.db = db

    async def confirm_pickup(
        self,
        task_id: int,
        quantity_received: int,
        invoice_url: str,
        notes: Optional[str] = None,
        user_id: int = None
    ):
        # Get the task and associated route card
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task or task.type != TaskType.PICKUP_FROM_SUBCONTRACTOR:
            raise ValueError("Invalid pickup task")

        route_card = task.route_card

        # Update task status
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        task.completed_by_id = user_id
        task.notes = notes

        # Add pickup details to route card
        if not hasattr(route_card, 'pickup_details'):
            route_card.pickup_details = []
        
        pickup_details = {
            "date": datetime.utcnow().isoformat(),
            "quantity_received": quantity_received,
            "invoice_url": invoice_url,
            "notes": notes,
            "user_id": user_id
        }
        route_card.pickup_details.append(pickup_details)

        # Update route card status and location
        route_card.current_location = RouteLocation.QC_AREA
        route_card.status = RouteStatus.AWAITING_QC

        # Create QC inspection task
        qc_task = Task(
            type=TaskType.QC_INSPECTION,
            description=f"Perform QC inspection for Route Card #{route_card.id}",
            route_card_id=route_card.id,
            due_date=datetime.utcnow(),  # Due immediately
            priority=1,  # High priority
            status=TaskStatus.PENDING,
            additional_data={
                "quantity_to_inspect": quantity_received,
                "subcontractor_invoice": invoice_url
            }
        )
        self.db.add(qc_task)

        self.db.commit()
        return task
