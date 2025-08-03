from datetime import datetime
from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.route_card import RouteCard, RouteStatus
from ..models.order import Order, OrderStatus
from ..models.task import Task, TaskType, TaskStatus
from ..schemas.route_card import RouteCardCreate
from ..services.notification_service import NotificationService
from ..services.audit_service import AuditService

class RouteCardService:
    def __init__(self, db: Session):
        self.db = db
        self.notification_service = NotificationService(db)
        self.audit_service = AuditService(db)

    def create_route_card(
        self,
        route_card_data: RouteCardCreate,
        user_id: int
    ) -> RouteCard:
        """Create a new route card and generate initial tasks."""
        # Get the order
        order = self.db.query(Order).filter(Order.id == route_card_data.order_id).first()
        if not order:
            raise ValueError("Order not found")

        # Create route card
        route_card = RouteCard(
            order_id=route_card_data.order_id,
            materials=route_card_data.materials,
            workstations=route_card_data.workstations,
            estimated_time=route_card_data.estimated_time,
            created_by_id=user_id,
            status=RouteStatus.DRAFT
        )
        
        self.db.add(route_card)
        self.db.commit()
        self.db.refresh(route_card)

        # Log the creation
        self.audit_service.create_log(
            user_id=user_id,
            action="CREATE",
            target_entity="RouteCard",
            target_id=str(route_card.id),
            details={
                "order_id": route_card_data.order_id,
                "status": RouteStatus.DRAFT
            }
        )

        return route_card

    def confirm_route_card(
        self,
        route_card_id: int,
        user_id: int
    ) -> RouteCard:
        """Confirm route card and create material preparation task."""
        route_card = self.db.query(RouteCard).filter(RouteCard.id == route_card_id).first()
        if not route_card:
            raise ValueError("Route card not found")

        # Update route card status
        old_status = route_card.status
        route_card.status = RouteStatus.CONFIRMED
        
        # Update order status
        route_card.order.status = OrderStatus.IN_PROGRESS

        # Create material preparation task
        materials_list = "\n".join([
            f"- {m['quantity']} {m['unit']} of Item #{m['item_id']}"
            for m in route_card.materials
        ])

        task = Task(
            type=TaskType.MATERIAL_PREPARATION,
            status=TaskStatus.PENDING,
            title=f"Prepare materials for Production Order #{route_card.order_id}",
            description=f"Please prepare the following materials:\n{materials_list}",
            assigned_to_id=None,  # Will be assigned by warehouse manager
            created_by_id=user_id,
            order_id=route_card.order_id,
            route_card_id=route_card.id
        )

        self.db.add(task)
        self.db.commit()
        self.db.refresh(route_card)

        # Log the status change
        self.audit_service.create_log(
            user_id=user_id,
            action="UPDATE",
            target_entity="RouteCard",
            target_id=str(route_card_id),
            details={
                "status_change": {
                    "from": old_status,
                    "to": RouteStatus.CONFIRMED
                },
                "order_id": route_card.order_id
            }
        )

        # Notify warehouse manager about material preparation task
        self.notification_service.create_notification(
            user_id=task.assigned_to_id if task.assigned_to_id else user_id,  # If no specific assignee, notify creator
            message=f"New material preparation task for Production Order #{route_card.order_id}",
            type="TASK",
            link=f"/tasks/{task.id}"
        )

        return route_card

    def update_route_card_status(
        self,
        route_card_id: int,
        new_status: str,
        user_id: int,
        notes: Optional[str] = None
    ) -> RouteCard:
        """Update the status of a route card."""
        route_card = self.db.query(RouteCard).filter(RouteCard.id == route_card_id).first()
        if not route_card:
            raise ValueError("Route card not found")

        old_status = route_card.status
        route_card.status = new_status
        if notes:
            route_card.notes = notes

        self.db.commit()
        self.db.refresh(route_card)

        # Log the status change
        self.audit_service.create_log(
            user_id=user_id,
            action="UPDATE",
            target_entity="RouteCard",
            target_id=str(route_card_id),
            details={
                "status_change": {
                    "from": old_status,
                    "to": new_status
                },
                "notes": notes
            }
        )

        # Notify relevant users based on the new status
        if new_status == RouteStatus.COMPLETED:
            # Notify order creator
            self.notification_service.create_notification(
                user_id=route_card.order.created_by_id,
                message=f"Route Card #{route_card_id} for Order #{route_card.order_id} has been completed",
                type="STATUS_UPDATE",
                link=f"/route-cards/{route_card_id}"
            )

        return route_card
