from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from ..models.warehouse_request import WarehouseRequest, WarehouseRequestItem, RequestStatus
from ..models.task import Task, TaskType, TaskStatus
from ..services.notification_service import NotificationService
from ..services.audit_service import AuditService

class WarehouseRequestService:
    def __init__(self, db: Session):
        self.db = db
        self.notification_service = NotificationService(db)
        self.audit_service = AuditService(db)

    def create_request(
        self,
        user_id: int,
        items: List[dict],
        request_type: str,
        priority: str = "normal",
        notes: Optional[str] = None
    ) -> WarehouseRequest:
        """Create a new warehouse request."""
        request = WarehouseRequest(
            created_by_id=user_id,
            request_type=request_type,
            priority=priority,
            notes=notes,
            status=RequestStatus.PENDING
        )
        
        self.db.add(request)
        self.db.flush()  # Get the request ID
        
        # Create request items
        for item in items:
            request_item = WarehouseRequestItem(
                request_id=request.id,
                item_id=item["item_id"],
                quantity=item["quantity"],
                status="pending"
            )
            self.db.add(request_item)
        
        self.db.commit()
        self.db.refresh(request)
        
        # Log the creation
        self.audit_service.create_log(
            user_id=user_id,
            action="CREATE",
            target_entity="WarehouseRequest",
            target_id=str(request.id),
            details={
                "type": request_type,
                "priority": priority,
                "item_count": len(items)
            }
        )
        
        # Notify warehouse staff
        self.notification_service.create_notification(
            user_id=None,  # TODO: Get warehouse manager's ID
            message=f"New {priority} priority warehouse request #{request.id}",
            type="WAREHOUSE_REQUEST",
            link=f"/warehouse-requests/{request.id}"
        )
        
        return request

    def update_request_status(
        self,
        request_id: int,
        status: str,
        user_id: int,
        notes: Optional[str] = None
    ) -> WarehouseRequest:
        """Update the status of a warehouse request."""
        request = self.db.query(WarehouseRequest).filter(WarehouseRequest.id == request_id).first()
        if not request:
            raise ValueError("Request not found")
        
        old_status = request.status
        request.status = status
        if notes:
            request.notes = notes
        
        self.db.commit()
        self.db.refresh(request)
        
        # Log the status change
        self.audit_service.create_log(
            user_id=user_id,
            action="UPDATE",
            target_entity="WarehouseRequest",
            target_id=str(request_id),
            details={
                "status_change": {
                    "from": old_status,
                    "to": status
                },
                "notes": notes
            }
        )
        
        # Send notifications based on status
        if status == RequestStatus.APPROVED:
            # Create picking task
            task = Task(
                type=TaskType.PICKING,
                status=TaskStatus.PENDING,
                title=f"Pick items for warehouse request #{request.id}",
                description=self._generate_picking_list(request),
                created_by_id=user_id,
                assigned_to_id=None  # Will be assigned by warehouse manager
            )
            self.db.add(task)
            self.db.commit()
            
            # Notify warehouse staff about picking task
            self.notification_service.create_notification(
                user_id=None,  # TODO: Get warehouse staff ID
                message=f"New picking task for request #{request.id}",
                type="TASK",
                link=f"/tasks/{task.id}"
            )
            
        elif status == RequestStatus.READY:
            # Notify requester
            self.notification_service.create_notification(
                user_id=request.created_by_id,
                message=f"Your warehouse request #{request.id} is ready for pickup",
                type="WAREHOUSE_REQUEST",
                link=f"/warehouse-requests/{request.id}"
            )
            
        elif status == RequestStatus.REJECTED:
            # Notify requester about rejection
            self.notification_service.create_notification(
                user_id=request.created_by_id,
                message=f"Your warehouse request #{request.id} has been rejected",
                type="WAREHOUSE_REQUEST",
                link=f"/warehouse-requests/{request.id}"
            )
        
        return request

    def _generate_picking_list(self, request: WarehouseRequest) -> str:
        """Generate a picking list description from request items."""
        items = []
        for item in request.items:
            items.append(f"- {item.quantity} units of Item #{item.item_id}")
        return "Please pick the following items:\n" + "\n".join(items)

    def update_item_status(
        self,
        request_id: int,
        item_id: int,
        status: str,
        user_id: int,
        quantity_fulfilled: Optional[int] = None,
        notes: Optional[str] = None
    ) -> WarehouseRequestItem:
        """Update the status of a specific item in a request."""
        item = self.db.query(WarehouseRequestItem).filter(
            WarehouseRequestItem.request_id == request_id,
            WarehouseRequestItem.id == item_id
        ).first()
        
        if not item:
            raise ValueError("Request item not found")
            
        old_status = item.status
        item.status = status
        if quantity_fulfilled is not None:
            item.quantity_fulfilled = quantity_fulfilled
        if notes:
            item.notes = notes
            
        self.db.commit()
        self.db.refresh(item)
        
        # Log the item status change
        self.audit_service.create_log(
            user_id=user_id,
            action="UPDATE",
            target_entity="WarehouseRequestItem",
            target_id=f"{request_id}/{item_id}",
            details={
                "status_change": {
                    "from": old_status,
                    "to": status
                },
                "quantity_fulfilled": quantity_fulfilled,
                "notes": notes
            }
        )
        
        # If item is marked as shortage, notify purchasing
        if status == "shortage":
            self.notification_service.create_notification(
                user_id=None,  # TODO: Get purchasing manager's ID
                message=f"Shortage reported for item #{item.item_id} in request #{request_id}",
                type="SHORTAGE",
                link=f"/warehouse-requests/{request_id}"
            )
            
        return item
