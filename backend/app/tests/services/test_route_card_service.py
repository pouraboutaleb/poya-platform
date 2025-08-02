import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from app.models.route_card import RouteCard, RouteStatus
from app.models.order import Order, OrderStatus
from app.models.task import Task, TaskType, TaskStatus
from app.services.route_card_service import RouteCardService
from app.schemas.route_card import RouteCardCreate

class TestRouteCardService:
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
    def route_card_service(self, db_session, notification_service, audit_service):
        """Create RouteCardService with mocked dependencies"""
        service = RouteCardService(db_session)
        service.notification_service = notification_service
        service.audit_service = audit_service
        return service

    def test_create_route_card(self, route_card_service, db_session):
        # Mock data
        order = Mock(id=1)
        db_session.query.return_value.filter.return_value.first.return_value = order
        
        route_card_data = RouteCardCreate(
            order_id=1,
            materials=[{"item_id": 1, "quantity": 10, "unit": "pcs"}],
            workstations=["ws1", "ws2"],
            estimated_time=120
        )
        
        # Execute
        result = route_card_service.create_route_card(route_card_data, user_id=1)
        
        # Assert
        assert result.order_id == 1
        assert result.status == RouteStatus.DRAFT
        assert len(result.materials) == 1
        
        # Verify audit log was created
        route_card_service.audit_service.create_log.assert_called_once_with(
            user_id=1,
            action="CREATE",
            target_entity="RouteCard",
            target_id=str(result.id),
            details={
                "order_id": 1,
                "status": RouteStatus.DRAFT
            }
        )

    def test_confirm_route_card(self, route_card_service, db_session):
        # Mock data
        route_card = Mock(
            id=1,
            order_id=1,
            status=RouteStatus.DRAFT,
            materials=[{"item_id": 1, "quantity": 10, "unit": "pcs"}],
            order=Mock(status=OrderStatus.DRAFT)
        )
        db_session.query.return_value.filter.return_value.first.return_value = route_card
        
        # Execute
        result = route_card_service.confirm_route_card(1, user_id=1)
        
        # Assert
        assert result.status == RouteStatus.CONFIRMED
        assert result.order.status == OrderStatus.IN_PROGRESS
        
        # Verify task was created
        task_created = False
        for call in db_session.add.call_args_list:
            obj = call[0][0]
            if isinstance(obj, Task):
                assert obj.type == TaskType.MATERIAL_PREPARATION
                assert obj.status == TaskStatus.PENDING
                task_created = True
                task = obj
        assert task_created
        
        # Verify audit log was created
        route_card_service.audit_service.create_log.assert_called_once_with(
            user_id=1,
            action="UPDATE",
            target_entity="RouteCard",
            target_id="1",
            details={
                "status_change": {
                    "from": RouteStatus.DRAFT,
                    "to": RouteStatus.CONFIRMED
                },
                "order_id": 1
            }
        )
        
        # Verify notification was sent
        route_card_service.notification_service.create_notification.assert_called_once_with(
            user_id=1,  # Since no assigned_to_id, should default to creator
            message=f"New material preparation task for Production Order #1",
            type="TASK",
            link=f"/tasks/{task.id}"
        )

    def test_update_route_card_status(self, route_card_service, db_session):
        # Mock data
        route_card = Mock(
            id=1,
            order_id=1,
            status=RouteStatus.CONFIRMED,
            order=Mock(created_by_id=2)
        )
        db_session.query.return_value.filter.return_value.first.return_value = route_card
        
        # Execute
        result = route_card_service.update_route_card_status(
            1,
            RouteStatus.COMPLETED,
            user_id=1,
            notes="Work completed"
        )
        
        # Assert
        assert result.status == RouteStatus.COMPLETED
        
        # Verify audit log
        route_card_service.audit_service.create_log.assert_called_once_with(
            user_id=1,
            action="UPDATE",
            target_entity="RouteCard",
            target_id="1",
            details={
                "status_change": {
                    "from": RouteStatus.CONFIRMED,
                    "to": RouteStatus.COMPLETED
                },
                "notes": "Work completed"
            }
        )
        
        # Verify notification to order creator
        route_card_service.notification_service.create_notification.assert_called_once_with(
            user_id=2,  # Order creator
            message="Route Card #1 for Order #1 has been completed",
            type="STATUS_UPDATE",
            link="/route-cards/1"
        )

    def test_invalid_status_transition(self, route_card_service, db_session):
        # Mock data
        route_card = Mock(
            id=1,
            status=RouteStatus.DRAFT
        )
        db_session.query.return_value.filter.return_value.first.return_value = route_card
        
        # Test invalid transition from DRAFT to COMPLETED
        with pytest.raises(ValueError, match="Invalid status transition"):
            route_card_service.update_route_card_status(1, RouteStatus.COMPLETED, user_id=1)
