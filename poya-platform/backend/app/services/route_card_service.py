from datetime import datetime
from sqlalchemy.orm import Session
from typing import List
from ..models.route_card import RouteCard, RouteStatus
from ..models.order import Order, OrderStatus
from ..models.task import Task, TaskType, TaskStatus
from ..schemas.route_card import RouteCardCreate

class RouteCardService:
    @staticmethod
    def create_route_card(
        db: Session,
        route_card_data: RouteCardCreate,
        user_id: int
    ) -> RouteCard:
        """Create a new route card and generate initial tasks."""
        # Get the order
        order = db.query(Order).filter(Order.id == route_card_data.order_id).first()
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
        
        db.add(route_card)
        db.commit()
        db.refresh(route_card)

        return route_card

    @staticmethod
    def confirm_route_card(
        db: Session,
        route_card_id: int,
        user_id: int
    ) -> RouteCard:
        """Confirm route card and create material preparation task."""
        route_card = db.query(RouteCard).filter(RouteCard.id == route_card_id).first()
        if not route_card:
            raise ValueError("Route card not found")

        # Update route card status
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

        db.add(task)
        db.commit()
        db.refresh(route_card)

        return route_card

    @staticmethod
    def get_route_card(
        db: Session,
        route_card_id: int
    ) -> RouteCard:
        """Get a route card by ID."""
        return db.query(RouteCard).filter(RouteCard.id == route_card_id).first()

    @staticmethod
    def get_production_orders(db: Session) -> List[Order]:
        """Get all active production orders."""
        return (
            db.query(Order)
            .filter(
                Order.order_type == "production",
                Order.status.in_(["draft", "submitted"])
            )
            .all()
        )
