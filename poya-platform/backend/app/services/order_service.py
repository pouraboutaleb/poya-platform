from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models.order import Order, OrderType, OrderStatus
from ..models.item import Item
from ..models.warehouse_request import WarehouseRequestItem
from ..models.task import Task, TaskType, TaskStatus
from ..schemas.order import OrderCreate

class OrderService:
    @staticmethod
    def create_shortage_order(
        db: Session,
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
        item = db.query(Item).filter(Item.id == item_id).first()
        if not item:
            raise ValueError("Item not found")

        # Get the request item for context
        request_item = db.query(WarehouseRequestItem).filter(
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

        db.add(order)
        db.commit()
        db.refresh(order)

        return order

    @staticmethod
    def update_order_status(
        db: Session,
        order_id: int,
        status: str,
        remarks: str = None
    ) -> Order:
        """
        Update an order's status and optionally add remarks.
        Also updates the related warehouse request item if needed.
        """
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise ValueError("Order not found")

        old_status = order.status
        order.status = status
        if remarks:
            order.remarks = remarks

        # If order is completed, update the warehouse request item
        if status == OrderStatus.COMPLETED and order.warehouse_request_item_id:
            request_item = db.query(WarehouseRequestItem).filter(
                WarehouseRequestItem.id == order.warehouse_request_item_id
            ).first()
            if request_item:
                request_item.status = "ready"
                request_item.quantity_fulfilled = order.quantity
                request_item.remarks = f"Fulfilled via {order.order_type} order #{order.id}"

        db.commit()
        db.refresh(order)
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

    @staticmethod
    def mark_order_purchased(
        db: Session,
        order_id: int,
        vendor_name: str,
        price: float,
        user_id: int
    ) -> Order:
        """
        Mark a procurement order as purchased and create a receiving task.
        """
        order = db.query(Order).filter(Order.id == order_id).first()
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
        
        db.add(task)
        db.commit()
        db.refresh(order)
        
        return order
