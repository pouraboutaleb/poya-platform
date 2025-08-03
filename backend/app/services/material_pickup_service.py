from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from sqlalchemy.sql import func
from ..models.task import Task, TaskType, TaskStatus
from ..models.route_card import RouteCard, RouteStatus, RouteLocation
from ..models.order import Order, OrderStatus

class MaterialPickupService:
    @staticmethod
    def get_active_pickup_tasks(db: Session) -> List[Task]:
        """Get all active material pickup tasks."""
        return (
            db.query(Task)
            .filter(
                Task.type == TaskType.MATERIAL_PICKUP,
                Task.status.in_([TaskStatus.NEW, TaskStatus.IN_PROGRESS])
            )
            .order_by(Task.priority.desc(), Task.created_at.asc())
            .all()
        )

    @staticmethod
    def confirm_pickup(
        db: Session,
        task_id: int,
        user_id: int
    ) -> Task:
        """
        Confirm material pickup and create delivery task.
        """
        # Get and validate the task
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise ValueError("Task not found")
        if task.type != TaskType.MATERIAL_PICKUP:
            raise ValueError("Invalid task type")

        # Get the route card
        route_card = (
            db.query(RouteCard)
            .filter(RouteCard.id == task.route_card_id)
            .first()
        )
        if not route_card:
            raise ValueError("Route card not found")

        # Update task status
        task.status = TaskStatus.COMPLETED
        task.completed_by_id = user_id
        task.completed_at = func.now()

        # Update route card status and location
        route_card.status = RouteStatus.MATERIALS_IN_TRANSIT
        route_card.current_location = RouteLocation.WITH_EXPEDITER

        # Get the first workstation
        current_workstation = route_card.workstations[0]
        is_subcontractor = current_workstation.get('is_subcontractor', False)

        # Create delivery task
        delivery_task = Task(
            type=TaskType.MATERIAL_PICKUP,  # Reuse the same type for simplicity
            status=TaskStatus.NEW,
            priority=task.priority,
            title=(
                f"Deliver materials for Production Order #{route_card.order_id} to "
                f"{'Subcontractor' if is_subcontractor else 'Workstation'}: "
                f"{current_workstation['name']}"
            ),
            description=(
                f"Please deliver the following materials:\n"
                f"{MaterialPickupService._format_materials_list(route_card.materials)}\n\n"
                f"Destination: {current_workstation['name']}\n"
                f"{current_workstation.get('description', '')}\n\n"
                f"Reference: Production Order #{route_card.order_id}"
            ),
            order_id=route_card.order_id,
            route_card_id=route_card.id,
            created_by_id=user_id
        )

        db.add(delivery_task)
        db.commit()
        db.refresh(task)
        db.refresh(delivery_task)
        db.refresh(route_card)

        return task

    @staticmethod
    def _format_materials_list(materials: List[dict]) -> str:
        """Format the materials list for task description."""
        return "\n".join([
            f"- {m['quantity']} {m['unit']} of Item #{m['item_id']}"
            for m in materials
        ])
