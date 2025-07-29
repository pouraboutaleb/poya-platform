from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy.orm import Session
from ..models.route_card import RouteCard, RouteLocation, RouteStatus
from ..models.task import Task, TaskStatus, TaskType

class QCDecision(str, Enum):
    APPROVE = "approve"
    REQUEST_REWORK = "request_rework"
    REQUEST_SCRAP = "request_scrap"

class QCInspectionService:
    def __init__(self, db: Session):
        self.db = db

    async def get_route_card_details(self, route_card_id: int):
        """Get full route card details including QC history"""
        route_card = self.db.query(RouteCard).filter(RouteCard.id == route_card_id).first()
        if not route_card:
            raise ValueError("Route card not found")
        
        # Get all QC logs and sort by date
        qc_logs = getattr(route_card, 'qc_logs', [])
        qc_logs.sort(key=lambda x: x.get('date'), reverse=True)
        
        return {
            "route_card": route_card,
            "qc_logs": qc_logs,
            "pickup_details": getattr(route_card, 'pickup_details', [])
        }

    async def process_qc_decision(
        self,
        task_id: int,
        decision: QCDecision,
        notes: Optional[str] = None,
        user_id: int = None
    ):
        # Get the task and associated route card
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task or task.type != TaskType.QC_INSPECTION:
            raise ValueError("Invalid QC inspection task")

        route_card = task.route_card

        # Add QC log entry
        if not hasattr(route_card, 'qc_logs'):
            route_card.qc_logs = []
        
        log_entry = {
            "date": datetime.utcnow().isoformat(),
            "decision": decision,
            "notes": notes,
            "user_id": user_id
        }
        route_card.qc_logs.append(log_entry)

        # Mark current task as complete
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        task.completed_by_id = user_id
        task.notes = notes

        # Handle decision-specific actions
        if decision == QCDecision.APPROVE:
            await self._handle_approval(route_card)
        elif decision == QCDecision.REQUEST_REWORK:
            await self._handle_rework_request(route_card)
        elif decision == QCDecision.REQUEST_SCRAP:
            await self._handle_scrap_request(route_card)

        self.db.commit()
        return task

    async def _handle_approval(self, route_card: RouteCard):
        """Handle approved QC inspection"""
        route_card.status = RouteStatus.COMPLETED
        route_card.current_location = RouteLocation.WAREHOUSE

        # Create warehouse stocking task
        stock_task = Task(
            type=TaskType.STOCK_FINISHED_PART,
            description=f"Stock completed part for Route Card #{route_card.id}",
            route_card_id=route_card.id,
            due_date=datetime.utcnow(),  # Due immediately
            priority=2,  # Medium priority
            status=TaskStatus.PENDING
        )
        self.db.add(stock_task)

    async def _handle_rework_request(self, route_card: RouteCard):
        """Handle rework request"""
        route_card.status = RouteStatus.NEEDS_REWORK
        
        # Create rework delivery task
        rework_task = Task(
            type=TaskType.DELIVER_FOR_REWORK,
            description=f"Return part for rework - Route Card #{route_card.id}",
            route_card_id=route_card.id,
            due_date=datetime.utcnow(),  # Due immediately
            priority=1,  # High priority
            status=TaskStatus.PENDING
        )
        self.db.add(rework_task)

    async def _handle_scrap_request(self, route_card: RouteCard):
        """Handle scrap request"""
        route_card.status = RouteStatus.AWAITING_SCRAP_APPROVAL
        
        # Create deviation permit review task
        review_task = Task(
            type=TaskType.REVIEW_SCRAP_REQUEST,
            description=f"Review scrap request for Route Card #{route_card.id}",
            route_card_id=route_card.id,
            due_date=datetime.utcnow(),  # Due immediately
            priority=1,  # High priority
            status=TaskStatus.PENDING,
            additional_data={
                "qc_logs": route_card.qc_logs,
                "pickup_details": route_card.pickup_details
            }
        )
        self.db.add(review_task)
