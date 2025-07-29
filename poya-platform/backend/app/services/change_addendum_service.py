from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from ..models.warehouse_request import WarehouseRequest, WarehouseRequestStatus, WarehouseRequestType
from ..models.change_request_approval import ChangeRequestApproval, ApprovalType, ApprovalLevel, ApprovalStatus
from ..models.task import Task, TaskStatus, TaskType
from ..models.user import User

class ChangeAddendumService:
    def __init__(self, db: Session):
        self.db = db

    async def create_change_addendum(
        self,
        original_request_id: int,
        description: str,
        impact_analysis: str,
        technical_justification: str,
        attachments: List[str],
        user_id: int
    ) -> ChangeRequestApproval:
        # Get original request
        original_request = self.db.query(WarehouseRequest).get(original_request_id)
        if not original_request:
            raise ValueError("Original warehouse request not found")

        # Create change request
        change_request = WarehouseRequest(
            project_name=f"Change Addendum - {original_request.project_name}",
            description=description,
            priority="high",
            status=WarehouseRequestStatus.AWAITING_APPROVAL,
            request_type=WarehouseRequestType.CHANGE_ADDENDUM,
            original_request_id=original_request_id,
            created_by_id=user_id
        )
        self.db.add(change_request)
        self.db.flush()  # Get ID for the change request

        # Create approval tracking
        approval = ChangeRequestApproval(
            request_type=ApprovalType.CHANGE_ADDENDUM,
            warehouse_request_id=change_request.id,
            submitted_by_id=user_id,
            description=description,
            attachments=attachments,
            impact_analysis=impact_analysis,
            technical_justification=technical_justification
        )
        self.db.add(approval)
        self.db.flush()

        # Create approval tasks in the correct sequence
        await self._create_approval_tasks(approval.id, change_request.id)

        self.db.commit()
        return approval

    async def update_approval(
        self,
        approval_id: int,
        level: ApprovalLevel,
        status: ApprovalStatus,
        user_id: int,
        comments: Optional[str] = None
    ):
        approval = self.db.query(ChangeRequestApproval).get(approval_id)
        if not approval:
            raise ValueError("Approval record not found")

        # Update approval status
        approval.update_approval(level, user_id, status, comments)
        
        # If approved and not the final level, create next approval task
        if status == ApprovalStatus.APPROVED:
            if level == ApprovalLevel.QC_MANAGER:
                await self._create_production_manager_task(approval_id, approval.warehouse_request_id)
            elif level == ApprovalLevel.PRODUCTION_MANAGER:
                await self._create_technical_manager_task(approval_id, approval.warehouse_request_id)

        # If rejected, update request status
        if status == ApprovalStatus.REJECTED:
            warehouse_request = approval.warehouse_request
            warehouse_request.status = WarehouseRequestStatus.CHANGES_REJECTED

        # If all approved, update request status
        if approval.is_completed and approval.is_approved:
            warehouse_request = approval.warehouse_request
            warehouse_request.status = WarehouseRequestStatus.CHANGES_APPROVED

        self.db.commit()
        return approval

    async def _create_approval_tasks(self, approval_id: int, request_id: int):
        """Create initial QC Manager approval task"""
        task = Task(
            type=TaskType.REVIEW_CHANGE_REQUEST,
            description=f"QC Review required for Change Addendum #{request_id}",
            priority=1,  # High priority
            status=TaskStatus.PENDING,
            additional_data={
                "approval_id": approval_id,
                "level": ApprovalLevel.QC_MANAGER
            }
        )
        self.db.add(task)

    async def _create_production_manager_task(self, approval_id: int, request_id: int):
        """Create Production Manager approval task"""
        task = Task(
            type=TaskType.REVIEW_CHANGE_REQUEST,
            description=f"Production Manager Review required for Change Addendum #{request_id}",
            priority=1,
            status=TaskStatus.PENDING,
            additional_data={
                "approval_id": approval_id,
                "level": ApprovalLevel.PRODUCTION_MANAGER
            }
        )
        self.db.add(task)

    async def _create_technical_manager_task(self, approval_id: int, request_id: int):
        """Create Technical Manager approval task"""
        task = Task(
            type=TaskType.REVIEW_CHANGE_REQUEST,
            description=f"Technical Manager Review required for Change Addendum #{request_id}",
            priority=1,
            status=TaskStatus.PENDING,
            additional_data={
                "approval_id": approval_id,
                "level": ApprovalLevel.TECHNICAL_MANAGER
            }
        )
        self.db.add(task)
