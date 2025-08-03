from sqlalchemy.orm import Session
from typing import List
from ..models.task import Task, TaskType, TaskStatus
from ..models.route_card import RouteCard, RouteStatus
from ..models.user import User

class MaterialPreparationService:
    @staticmethod
    def get_active_preparation_tasks(db: Session) -> List[Task]:
        """Get all active material preparation tasks."""
        return (
            db.query(Task)
            .filter(
                Task.type == TaskType.MATERIAL_PREPARATION,
                Task.status.in_([TaskStatus.NEW, TaskStatus.IN_PROGRESS])
            )
            .order_by(Task.priority.desc(), Task.created_at.asc())
            .all()
        )

    @staticmethod
    def mark_materials_prepared(
        db: Session,
        task_id: int,
        user_id: int
    ) -> Task:
        """Mark materials as prepared and create pickup task."""
        # Get the task and validate
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise ValueError("Task not found")
        if task.type != TaskType.MATERIAL_PREPARATION:
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

        # Create pickup task for buyer/expediter
        materials_list = "\n".join([
            f"- {m['quantity']} {m['unit']} of Item #{m['item_id']}"
            for m in route_card.materials
        ])

        pickup_task = Task(
            type=TaskType.MATERIAL_PICKUP,
            status=TaskStatus.NEW,
            priority=task.priority,  # Maintain same priority
            title=f"Pick up materials for Production Order #{route_card.order_id}",
            description=(
                f"Materials are prepared and ready for pickup:\n{materials_list}\n\n"
                f"Location: Warehouse Material Preparation Area\n"
                f"Reference: Material Preparation Task #{task.id}"
            ),
            order_id=route_card.order_id,
            route_card_id=route_card.id,
            created_by_id=user_id
        )

        db.add(pickup_task)
        db.commit()
        db.refresh(task)
        db.refresh(pickup_task)

        return task
