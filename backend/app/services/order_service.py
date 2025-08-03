from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.order import Order, OrderType, OrderStatus
from ..models.item import Item
from ..models.warehouse_request import WarehouseRequestItem
from ..models.task import Task, TaskType, TaskStatus
from ..schemas.order import OrderCreate
from ..services.notification_service import NotificationService
from ..services.audit_service import AuditService
from ..services.user_role_service import UserRoleService

class OrderService:
    def __init__(self, db: Session):
        self.db = db
        self.notification_service = NotificationService(db)
        self.audit_service = AuditService(db)
        self.user_role_service = UserRoleService(db)
        self.audit_service = AuditService(db)

    def create_shortage_order(
        self,
        item_id: int,
        warehouse_request_item_id: int,
        created_by_id: int,
        quantity: int,
        priority: str = "normal"
    ) -> Order:
        """
        Create a new order for a shortage item.
        Automatically determines if it should be a procurement or production order.
        """
        # Get the item details to determine order type
        item = self.db.query(Item).filter(Item.id == item_id).first()
        if not item:
            raise ValueError("Item not found")

        # Get the request item for context
        request_item = self.db.query(WarehouseRequestItem).filter(
            WarehouseRequestItem.id == warehouse_request_item_id
        ).first()
        if not request_item:
            raise ValueError("Warehouse request item not found")

        # Determine order type based on item category
        # You might want to add more sophisticated logic here
        order_type = (
            OrderType.PRODUCTION
            if item.category.name.lower() in ["manufactured", "production", "internal"]
            else OrderType.PROCUREMENT
        )

        # Create the order
        order = Order(
            order_type=order_type,
            status=OrderStatus.DRAFT,
            priority=priority,
            quantity=quantity,
            remarks=f"Auto-generated due to shortage in warehouse request #{request_item.request_id}",
            required_date=datetime.now() + timedelta(days=7),  # Default to 7 days
            created_by_id=created_by_id,
            item_id=item_id,
            warehouse_request_item_id=warehouse_request_item_id
        )

        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)

        # Log the creation
        self.audit_service.create_log(
            user_id=created_by_id,
            action="CREATE",
            target_entity="Order",
            target_id=str(order.id),
            details={
                "type": order_type,
                "item_id": item_id,
                "quantity": quantity,
                "warehouse_request_item_id": warehouse_request_item_id
            }
        )

        # Notify based on order type
        if order_type == OrderType.PROCUREMENT:
            # Notify procurement team
            procurement_lead = self.user_role_service.get_procurement_team_lead()
            if procurement_lead:
                self.notification_service.create_notification(
                    user_id=procurement_lead.id,
                    message=f"New procurement order #{order.id} created for {quantity} units of item #{item_id}",
                    type="ORDER",
                    link=f"/orders/{order.id}"
                )
        else:  # PRODUCTION
            # Notify production planning
            production_planner = self.user_role_service.get_production_planner()
            if production_planner:
                self.notification_service.create_notification(
                    user_id=production_planner.id,
                    message=f"New production order #{order.id} created for {quantity} units of item #{item_id}",
                    type="ORDER",
                    link=f"/orders/{order.id}"
                )

        return order

    def update_order_status(
        self,
        order_id: int,
        status: str,
        user_id: int,
        remarks: str = None
    ) -> Order:
        """
        Update an order's status and optionally add remarks.
        Also updates the related warehouse request item if needed.
        """
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise ValueError("Order not found")

        old_status = order.status
        order.status = status
        if remarks:
            order.remarks = remarks

        # If order is completed, update the warehouse request item
        if status == OrderStatus.COMPLETED and order.warehouse_request_item_id:
            request_item = self.db.query(WarehouseRequestItem).filter(
                WarehouseRequestItem.id == order.warehouse_request_item_id
            ).first()
            if request_item:
                request_item.status = "ready"
                request_item.quantity_fulfilled = order.quantity
                request_item.remarks = f"Fulfilled via {order.order_type} order #{order.id}"

        self.db.commit()
        self.db.refresh(order)

        # Log the status change
        self.audit_service.create_log(
            user_id=user_id,
            action="UPDATE",
            target_entity="Order",
            target_id=str(order_id),
            details={
                "status_change": {
                    "from": old_status,
                    "to": status
                },
                "remarks": remarks
            }
        )

        # Send notifications based on the new status
        if status == OrderStatus.COMPLETED:
            # Notify the creator
            self.notification_service.create_notification(
                user_id=order.created_by_id,
                message=f"Order #{order.id} has been completed",
                type="ORDER",
                link=f"/orders/{order.id}"
            )

            # If this was for a warehouse request, notify the requestor
            if order.warehouse_request_item_id and request_item:
                self.notification_service.create_notification(
                    user_id=request_item.request.created_by_id,
                    message=f"Your warehouse request #{request_item.request_id} has been fulfilled",
                    type="WAREHOUSE_REQUEST",
                    link=f"/warehouse-requests/{request_item.request_id}"
                )

        elif status == OrderStatus.CANCELLED:
            # Notify relevant parties about cancellation
            stakeholders = [order.created_by_id]
            if order.assigned_to_id:
                stakeholders.append(order.assigned_to_id)
            
            for user_id in stakeholders:
                self.notification_service.create_notification(
                    user_id=user_id,
                    message=f"Order #{order.id} has been cancelled",
                    type="ORDER",
                    link=f"/orders/{order.id}"
                )

        return order

    @staticmethod
    def get_related_orders(
        db: Session,
        warehouse_request_item_id: int
    ) -> list[Order]:
        """Get all orders related to a specific warehouse request item."""
        return db.query(Order).filter(
            Order.warehouse_request_item_id == warehouse_request_item_id
        ).all()
    
    @staticmethod
    def get_procurement_orders(db: Session) -> list[Order]:
        """Get all active procurement orders."""
        return db.query(Order).filter(
            Order.order_type == OrderType.PROCUREMENT,
            Order.status.in_([OrderStatus.DRAFT, OrderStatus.SUBMITTED])
        ).all()

    def mark_order_purchased(
        self,
        order_id: int,
        vendor_name: str,
        price: float,
        user_id: int
    ) -> Order:
        """
        Mark a procurement order as purchased and create a receiving task.
        """
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise ValueError("Order not found")
        
        if order.order_type != OrderType.PROCUREMENT:
            raise ValueError("Only procurement orders can be marked as purchased")
        
        # Update order with purchase details
        order.vendor_name = vendor_name
        order.price = int(price * 100)  # Convert to cents
        order.status = OrderStatus.IN_PROGRESS
        
        # Create a receiving task for the warehouse
        task = Task(
            type=TaskType.RECEIVING,
            status=TaskStatus.PENDING,
            title=f"Receive order #{order.id} from {vendor_name}",
            description=f"Receive {order.quantity} units of item #{order.item_id}",
            assigned_to_id=None,  # Will be assigned by warehouse manager
            created_by_id=user_id,
            order_id=order.id
        )
        
        self.db.add(task)
        
        # Log the purchase
        self.audit_service.create_log(
            user_id=user_id,
            action="PURCHASE",
            target_entity="Order",
            target_id=str(order_id),
            details={
                "vendor": vendor_name,
                "price": price,
                "quantity": order.quantity,
                "item_id": order.item_id
            }
        )
        
        # Notify warehouse team about incoming delivery
        warehouse_manager = self.user_role_service.get_warehouse_manager()
        if warehouse_manager:
            self.notification_service.create_notification(
                user_id=warehouse_manager.id,
                message=f"New delivery expected: Order #{order.id} from {vendor_name}",
                type="RECEIVING",
                link=f"/tasks/{task.id}"
            )
        
        self.db.commit()
        self.db.refresh(order)
        
        return order
