import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.warehouse_request import WarehouseRequest, WarehouseRequestItem, RequestStatus
from app.models.task import Task, TaskType
from app.models.audit import AuditLog
from app.models.notification import Notification
from app.main import app
from app.core.security import create_access_token

class TestWarehouseRequestAPI:
    @pytest.fixture
    def client(self):
        return TestClient(app)

    @pytest.fixture
    def db_session(self, mocker):
        """Create a test database session"""
        # This would typically use a test database
        return mocker.Mock(spec=Session)

    @pytest.fixture
    def auth_headers(self):
        """Create authentication headers for test user"""
        access_token = create_access_token({"sub": "1"})  # User ID 1
        return {"Authorization": f"Bearer {access_token}"}

    def test_create_warehouse_request_flow(self, client, db_session, auth_headers):
        """Test the complete flow of creating a warehouse request"""
        # Test data
        request_data = {
            "items": [
                {"item_id": 1, "quantity": 10},
                {"item_id": 2, "quantity": 5}
            ],
            "request_type": "production",
            "priority": "high",
            "notes": "Urgent materials needed"
        }

        # Make the request
        response = client.post(
            "/api/v1/warehouse-requests",
            json=request_data,
            headers=auth_headers
        )

        # Assert response
        assert response.status_code == 201
        created_request = response.json()
        assert created_request["status"] == RequestStatus.PENDING
        assert len(created_request["items"]) == 2

        # Verify database entries
        request_id = created_request["id"]

        # Check audit log was created
        audit_logs = db_session.query(AuditLog).filter(
            AuditLog.target_entity == "WarehouseRequest",
            AuditLog.target_id == str(request_id)
        ).all()
        assert len(audit_logs) == 1
        assert audit_logs[0].action == "CREATE"

        # Check notification was created
        notifications = db_session.query(Notification).filter(
            Notification.type == "WAREHOUSE_REQUEST"
        ).all()
        assert len(notifications) == 1
        assert f"request #{request_id}" in notifications[0].message

        # Now test approving the request
        approval_response = client.put(
            f"/api/v1/warehouse-requests/{request_id}/status",
            json={"status": "approved", "notes": "Approved by warehouse manager"},
            headers=auth_headers
        )

        assert approval_response.status_code == 200
        approved_request = approval_response.json()
        assert approved_request["status"] == RequestStatus.APPROVED

        # Verify picking task was created
        tasks = db_session.query(Task).filter(
            Task.type == TaskType.PICKING
        ).all()
        assert len(tasks) == 1
        picking_task = tasks[0]
        assert picking_task.status == "pending"

        # Verify additional audit log
        audit_logs = db_session.query(AuditLog).filter(
            AuditLog.target_entity == "WarehouseRequest",
            AuditLog.target_id == str(request_id)
        ).all()
        assert len(audit_logs) == 2  # Creation + Status update

        # Verify notifications were sent
        notifications = db_session.query(Notification).all()
        assert len(notifications) == 2  # Initial + Picking task notification

class TestRouteCardAPI:
    @pytest.fixture
    def client(self):
        return TestClient(app)

    @pytest.fixture
    def auth_headers(self):
        access_token = create_access_token({"sub": "1"})
        return {"Authorization": f"Bearer {access_token}"}

    def test_route_card_lifecycle(self, client, db_session, auth_headers):
        """Test the complete lifecycle of a route card"""
        # Create route card
        route_card_data = {
            "order_id": 1,
            "materials": [
                {"item_id": 1, "quantity": 10, "unit": "pcs"}
            ],
            "workstations": ["ws1", "ws2"],
            "estimated_time": 120
        }

        response = client.post(
            "/api/v1/route-cards",
            json=route_card_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        route_card = response.json()
        route_card_id = route_card["id"]

        # Verify audit log
        audit_logs = db_session.query(AuditLog).filter(
            AuditLog.target_entity == "RouteCard",
            AuditLog.target_id == str(route_card_id)
        ).all()
        assert len(audit_logs) == 1

        # Confirm route card
        confirm_response = client.post(
            f"/api/v1/route-cards/{route_card_id}/confirm",
            headers=auth_headers
        )

        assert confirm_response.status_code == 200
        confirmed_card = confirm_response.json()
        assert confirmed_card["status"] == "confirmed"

        # Verify material preparation task was created
        tasks = db_session.query(Task).filter(
            Task.type == TaskType.MATERIAL_PREPARATION,
            Task.route_card_id == route_card_id
        ).all()
        assert len(tasks) == 1

        # Verify notifications
        notifications = db_session.query(Notification).filter(
            Notification.type == "TASK"
        ).all()
        assert len(notifications) == 1
        assert "material preparation" in notifications[0].message.lower()

        # Complete route card
        complete_response = client.put(
            f"/api/v1/route-cards/{route_card_id}/status",
            json={"status": "completed", "notes": "All work completed"},
            headers=auth_headers
        )

        assert complete_response.status_code == 200
        completed_card = complete_response.json()
        assert completed_card["status"] == "completed"

        # Verify final audit logs and notifications
        audit_logs = db_session.query(AuditLog).filter(
            AuditLog.target_entity == "RouteCard",
            AuditLog.target_id == str(route_card_id)
        ).all()
        assert len(audit_logs) == 3  # Creation + Confirmation + Completion

        notifications = db_session.query(Notification).all()
        assert len(notifications) == 2  # Task notification + Completion notification
