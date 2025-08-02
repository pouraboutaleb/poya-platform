import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from app.models.order import Order, OrderType, OrderStatus
from app.models.warehouse_request import WarehouseRequestItem
from app.models.task import Task, TaskType, TaskStatus
from app.services.order_service import OrderService

class TestOrderService:
    @pytest.fixture
    def db_session(self):
        """Mock database session"""
        return Mock(spec=Session)

    @pytest.fixture
    def notification_service(self):
        """Mock notification service"""
        return Mock()

    @pytest.fixture
    def audit_service(self):
        """Mock audit service"""
        return Mock()

    @pytest.fixture
    def order_service(self, db_session, notification_service, audit_service):
        """Create OrderService with mocked dependencies"""
        service = OrderService(db_session)
        service.notification_service = notification_service
        service.audit_service = audit_service
        return service

    def test_create_shortage_order_procurement(self, order_service, db_session):
        # Mock data
        item = Mock(id=1, category=Mock(name="purchased"))
        request_item = Mock(id=1, request_id=1)
        db_session.query.return_value.filter.return_value.first.side_effect = [item, request_item]
        
        # Execute
        result = order_service.create_shortage_order(
            item_id=1,
            warehouse_request_item_id=1,
            created_by_id=1,
            quantity=10
        )
        
        # Assert
        assert result.order_type == OrderType.PROCUREMENT
        assert result.status == OrderStatus.DRAFT
        assert result.quantity == 10
        
        # Verify audit log
        order_service.audit_service.create_log.assert_called_once_with(
            user_id=1,
            action="CREATE",
            target_entity="Order",
            target_id=str(result.id),
            details={
                "type": OrderType.PROCUREMENT,
                "item_id": 1,
                "quantity": 10,
                "warehouse_request_item_id": 1
            }
        )
        
        # Verify notification
        order_service.notification_service.create_notification.assert_called_once()

    def test_update_order_status_completion(self, order_service, db_session):
        # Mock data
        order = Mock(
            id=1,
            status=OrderStatus.IN_PROGRESS,
            warehouse_request_item_id=1,
            quantity=10,
            created_by_id=2
        )
        request_item = Mock(id=1, request=Mock(created_by_id=3))
        db_session.query.return_value.filter.return_value.first.side_effect = [order, request_item]
        
        # Execute
        result = order_service.update_order_status(
            order_id=1,
            status=OrderStatus.COMPLETED,
            user_id=1,
            remarks="Order fulfilled"
        )
        
        # Assert
        assert result.status == OrderStatus.COMPLETED
        
        # Verify warehouse request item was updated
        assert request_item.status == "ready"
        assert request_item.quantity_fulfilled == 10
        
        # Verify audit log
        order_service.audit_service.create_log.assert_called_once_with(
            user_id=1,
            action="UPDATE",
            target_entity="Order",
            target_id="1",
            details={
                "status_change": {
                    "from": OrderStatus.IN_PROGRESS,
                    "to": OrderStatus.COMPLETED
                },
                "remarks": "Order fulfilled"
            }
        )
        
        # Verify notifications
        assert order_service.notification_service.create_notification.call_count == 2
        # Check notifications to order creator and request creator
        notification_calls = order_service.notification_service.create_notification.call_args_list
        assert notification_calls[0][1]["user_id"] == 2  # Order creator
        assert notification_calls[1][1]["user_id"] == 3  # Request creator

    def test_mark_order_purchased(self, order_service, db_session):
        # Mock data
        order = Mock(
            id=1,
            order_type=OrderType.PROCUREMENT,
            item_id=1,
            quantity=10
        )
        db_session.query.return_value.filter.return_value.first.return_value = order
        
        # Execute
        result = order_service.mark_order_purchased(
            order_id=1,
            vendor_name="Test Vendor",
            price=100.50,
            user_id=1
        )
        
        # Assert
        assert result.status == OrderStatus.IN_PROGRESS
        assert result.vendor_name == "Test Vendor"
        assert result.price == 10050  # Converted to cents
        
        # Verify receiving task was created
        task_created = False
        for call in db_session.add.call_args_list:
            obj = call[0][0]
            if isinstance(obj, Task):
                assert obj.type == TaskType.RECEIVING
                assert obj.status == TaskStatus.PENDING
                task_created = True
                task = obj
        assert task_created
        
        # Verify audit log
        order_service.audit_service.create_log.assert_called_once_with(
            user_id=1,
            action="PURCHASE",
            target_entity="Order",
            target_id="1",
            details={
                "vendor": "Test Vendor",
                "price": 100.50,
                "quantity": 10,
                "item_id": 1
            }
        )
        
        # Verify notification
        order_service.notification_service.create_notification.assert_called_once_with(
            user_id=None,  # Warehouse manager ID to be configured
            message="New delivery expected: Order #1 from Test Vendor",
            type="RECEIVING",
            link=f"/tasks/{task.id}"
        )

    def test_invalid_order_purchase(self, order_service, db_session):
        # Mock data
        order = Mock(
            id=1,
            order_type=OrderType.PRODUCTION  # Not a procurement order
        )
        db_session.query.return_value.filter.return_value.first.return_value = order
        
        # Test invalid purchase attempt for production order
        with pytest.raises(ValueError, match="Only procurement orders can be marked as purchased"):
            order_service.mark_order_purchased(1, "Test Vendor", 100.0, user_id=1)
