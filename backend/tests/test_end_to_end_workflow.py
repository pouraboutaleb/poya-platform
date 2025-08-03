import pytest
import httpx
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
import sys
from pathlib import Path

# Add the parent directory to the Python path to import the app
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load test environment
import dotenv
dotenv.load_dotenv(".env.test")

# Test Configuration
TEST_BASE_URL = "http://localhost:8000"
TEST_DATABASE_URL = "sqlite:///./test_mrdpol_core_platform.db"


class TestClient:
    """Enhanced test client for API testing"""
    
    def __init__(self, base_url: str = TEST_BASE_URL):
        self.base_url = base_url
        self.access_token: Optional[str] = None
        self.client = httpx.AsyncClient(base_url=base_url, timeout=30.0)
    
    async def close(self):
        await self.client.aclose()
    
    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers
    
    async def login(self, email: str = "admin@mrdpol.com", password: str = "admin123"):
        """Login and store access token"""
        data = {
            "username": email,
            "password": password
        }
        response = await self.client.post(
            "/api/v1/auth/token",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        response.raise_for_status()
        token_data = response.json()
        self.access_token = token_data["access_token"]
        return token_data
    
    async def get(self, url: str) -> httpx.Response:
        response = await self.client.get(url, headers=self._get_headers())
        return response
    
    async def post(self, url: str, data: Any = None, json: Any = None) -> httpx.Response:
        response = await self.client.post(
            url, 
            data=data, 
            json=json, 
            headers=self._get_headers()
        )
        return response
    
    async def put(self, url: str, json: Any = None) -> httpx.Response:
        response = await self.client.put(url, json=json, headers=self._get_headers())
        return response
    
    async def delete(self, url: str) -> httpx.Response:
        response = await self.client.delete(url, headers=self._get_headers())
        return response


@pytest.fixture
async def test_client():
    """Create and configure test client"""
    client = TestClient()
    await client.login()
    yield client
    await client.close()


@pytest.fixture
def test_db():
    """Create test database session"""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Import all models to ensure tables are created
    from app.models import user, item, warehouse_request, order, task, route_card, notification, audit
    from app.db.session import Base
    
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    # Initialize basic test data
    _setup_test_data(db)
    
    yield db
    
    db.close()
    # Clean up - drop all tables
    Base.metadata.drop_all(bind=engine)


def _setup_test_data(db):
    """Setup minimal test data"""
    from app.models.user import User, Role
    from app.models.item import Item
    from app.models.item_category import ItemCategory
    from app.core.security import get_password_hash
    
    # Create roles
    roles_data = [
        ("admin", "System administrator"),
        ("warehouse_manager", "Warehouse manager"),
        ("warehouse_staff", "Warehouse staff"),
        ("purchasing_manager", "Purchasing manager"),
        ("procurement_lead", "Procurement team lead"),
        ("production_manager", "Production manager"),
        ("production_planner", "Production planner"),
        ("qc_manager", "QC manager"),
        ("qc_inspector", "QC inspector"),
        ("user", "Regular user")
    ]
    
    for role_name, description in roles_data:
        role = Role(name=role_name, description=description)
        db.add(role)
    
    db.commit()
    
    # Create test users
    admin_role = db.query(Role).filter(Role.name == "admin").first()
    warehouse_mgr_role = db.query(Role).filter(Role.name == "warehouse_manager").first()
    production_mgr_role = db.query(Role).filter(Role.name == "production_manager").first()
    qc_mgr_role = db.query(Role).filter(Role.name == "qc_manager").first()
    
    users_data = [
        ("admin@mrdpol.com", "Admin User", True, [admin_role, warehouse_mgr_role]),
        ("warehouse@mrdpol.com", "Warehouse Manager", True, [warehouse_mgr_role]),
        ("production@mrdpol.com", "Production Manager", False, [production_mgr_role]),
        ("qc@mrdpol.com", "QC Manager", False, [qc_mgr_role]),
    ]
    
    for email, name, is_warehouse, user_roles in users_data:
        user = User(
            email=email,
            full_name=name,
            hashed_password=get_password_hash("password123"),
            is_active=True,
            is_warehouse_staff=is_warehouse
        )
        user.roles.extend(user_roles)
        db.add(user)
    
    db.commit()
    
    # Create test item category and items
    category = ItemCategory(name="Test Parts", description="Test category")
    db.add(category)
    db.commit()
    
    items_data = [
        ("PART001", "Test Part 1", "A test part that needs production"),
        ("PART002", "Test Part 2", "Another test part"),
    ]
    
    for code, name, desc in items_data:
        item = Item(
            item_code=code,
            name=name,
            description=desc,
            category_id=category.id
        )
        db.add(item)
    
    db.commit()


class WorkflowTestData:
    """Container for workflow test data"""
    def __init__(self):
        self.warehouse_request_id: Optional[int] = None
        self.order_id: Optional[int] = None
        self.route_card_id: Optional[int] = None
        self.tasks: Dict[str, int] = {}
        self.notifications: list = []
        self.audit_logs: list = []


@pytest.mark.asyncio
async def test_complete_production_workflow(test_client: TestClient, test_db):
    """
    Complete end-to-end test of the production workflow
    Tests the journey from warehouse request to final QC approval
    """
    workflow_data = WorkflowTestData()
    
    print("🚀 Starting End-to-End Production Workflow Test")
    
    # Step 1: Create Warehouse Request
    await _step_1_create_warehouse_request(test_client, workflow_data, test_db)
    
    # Step 2: Verify Order Creation
    await _step_2_verify_order_creation(test_client, workflow_data, test_db)
    
    # Step 3: Create and Confirm Route Card
    await _step_3_create_route_card(test_client, workflow_data, test_db)
    
    # Step 4: Material Preparation
    await _step_4_material_preparation(test_client, workflow_data, test_db)
    
    # Step 5: Material Pickup by Expediter
    await _step_5_material_pickup(test_client, workflow_data, test_db)
    
    # Step 6: Delivery to Subcontractor
    await _step_6_delivery_to_subcontractor(test_client, workflow_data, test_db)
    
    # Step 7: Production Follow-up
    await _step_7_production_followup(test_client, workflow_data, test_db)
    
    # Step 8: Part Pickup from Subcontractor
    await _step_8_part_pickup(test_client, workflow_data, test_db)
    
    # Step 9: QC Inspection and Approval
    await _step_9_qc_inspection(test_client, workflow_data, test_db)
    
    # Step 10: Final Verification
    await _step_10_final_verification(test_client, workflow_data, test_db)
    
    print("✅ End-to-End Production Workflow Test Completed Successfully!")


async def _step_1_create_warehouse_request(client: TestClient, data: WorkflowTestData, db):
    """Step 1: Create a warehouse request for an item that needs production"""
    print("📝 Step 1: Creating warehouse request...")
    
    # Get item that will need production
    item_response = await client.get("/api/v1/items")
    assert item_response.status_code == 200
    items = item_response.json()
    test_item = items[0]  # Use first item
    
    # Create warehouse request
    request_data = {
        "project_name": "E2E Test Project",
        "description": "End-to-end test warehouse request",
        "priority": "high",
        "requested_delivery_date": (datetime.now() + timedelta(days=7)).isoformat(),
        "request_items": [
            {
                "item_id": test_item["id"],
                "quantity_requested": 10,
                "remarks": "Test item for production"
            }
        ]
    }
    
    response = await client.post("/api/v1/warehouse/warehouse-requests", json=request_data)
    assert response.status_code == 201, f"Failed to create warehouse request: {response.text}"
    
    request = response.json()
    data.warehouse_request_id = request["id"]
    
    print(f"✅ Warehouse request created with ID: {data.warehouse_request_id}")
    
    # Verify notification was sent to warehouse manager
    notifications_response = await client.get("/api/v1/notifications/me")
    assert notifications_response.status_code == 200
    notifications = notifications_response.json()
    
    # Should have notification about new warehouse request
    new_request_notifications = [n for n in notifications if "warehouse request" in n["message"].lower()]
    assert len(new_request_notifications) > 0, "No notification sent for warehouse request"
    
    print("✅ Notification verified for warehouse request creation")


async def _step_2_verify_order_creation(client: TestClient, data: WorkflowTestData, db):
    """Step 2: Verify that a production order was automatically created"""
    print("🏭 Step 2: Verifying automatic order creation...")
    
    # Mark item as shortage to trigger order creation
    request_response = await client.get(f"/api/v1/warehouse/warehouse-requests/{data.warehouse_request_id}")
    assert request_response.status_code == 200
    request = request_response.json()
    
    request_item = request["request_items"][0]
    item_id = request_item["item_id"]
    
    # Create shortage order
    shortage_data = {
        "item_id": item_id,
        "quantity": request_item["quantity_requested"],
        "priority": "high",
        "required_date": (datetime.now() + timedelta(days=5)).isoformat()
    }
    
    order_response = await client.post(
        f"/api/v1/warehouse-requests/{request_item['id']}/shortage",
        json=shortage_data
    )
    assert order_response.status_code == 201, f"Failed to create shortage order: {order_response.text}"
    
    order = order_response.json()
    data.order_id = order["id"]
    
    # Verify it's a production order
    assert order["order_type"] == "production", f"Expected production order, got {order['order_type']}"
    assert order["status"] == "draft", f"Expected draft status, got {order['status']}"
    
    print(f"✅ Production order created with ID: {data.order_id}")
    
    # Verify notification was sent to production planner
    notifications_response = await client.get("/api/v1/notifications/me")
    assert notifications_response.status_code == 200
    notifications = notifications_response.json()
    
    production_notifications = [n for n in notifications if "production order" in n["message"].lower()]
    assert len(production_notifications) > 0, "No notification sent for production order"
    
    print("✅ Production order notification verified")


async def _step_3_create_route_card(client: TestClient, data: WorkflowTestData, db):
    """Step 3: Create and confirm a multi-step route card"""
    print("🗺️ Step 3: Creating and confirming route card...")
    
    # Create route card for the production order
    route_card_data = {
        "order_id": data.order_id,
        "materials": [
            {"material_code": "MAT001", "quantity": 5, "unit": "kg"},
            {"material_code": "MAT002", "quantity": 2, "unit": "pieces"}
        ],
        "workstations": [
            {"station": "Cutting", "estimated_time": 2.5, "subcontractor": None},
            {"station": "Machining", "estimated_time": 4.0, "subcontractor": "ABC Machining"},
            {"station": "Assembly", "estimated_time": 1.5, "subcontractor": None},
            {"station": "Finishing", "estimated_time": 3.0, "subcontractor": "XYZ Finishing"}
        ],
        "estimated_time": 11.0
    }
    
    response = await client.post("/api/v1/route-cards", json=route_card_data)
    assert response.status_code == 201, f"Failed to create route card: {response.text}"
    
    route_card = response.json()
    data.route_card_id = route_card["id"]
    
    print(f"✅ Route card created with ID: {data.route_card_id}")
    
    # Confirm the route card
    confirm_response = await client.post(f"/api/v1/route-cards/{data.route_card_id}/confirm")
    assert confirm_response.status_code == 200, f"Failed to confirm route card: {confirm_response.text}"
    
    confirmed_route_card = confirm_response.json()
    assert confirmed_route_card["status"] == "confirmed", f"Expected confirmed status, got {confirmed_route_card['status']}"
    
    print("✅ Route card confirmed")
    
    # Verify material preparation task was created
    tasks_response = await client.get("/api/v1/material-preparation/preparation-tasks")
    assert tasks_response.status_code == 200
    tasks = tasks_response.json()
    
    prep_tasks = [t for t in tasks if str(data.route_card_id) in t.get("description", "")]
    assert len(prep_tasks) > 0, "No material preparation task created"
    
    data.tasks["material_preparation"] = prep_tasks[0]["id"]
    print(f"✅ Material preparation task created with ID: {data.tasks['material_preparation']}")


async def _step_4_material_preparation(client: TestClient, data: WorkflowTestData, db):
    """Step 4: Complete material preparation"""
    print("📦 Step 4: Completing material preparation...")
    
    task_id = data.tasks["material_preparation"]
    
    # Mark materials as prepared
    response = await client.post(f"/api/v1/material-preparation/preparation-tasks/{task_id}/complete")
    assert response.status_code == 200, f"Failed to complete material preparation: {response.text}"
    
    completed_task = response.json()
    assert completed_task["status"] == "completed", f"Expected completed status, got {completed_task['status']}"
    
    print("✅ Material preparation completed")
    
    # Verify pickup task was created
    pickup_tasks_response = await client.get("/api/v1/material-pickup/pickup-tasks")
    assert pickup_tasks_response.status_code == 200
    pickup_tasks = pickup_tasks_response.json()
    
    new_pickup_tasks = [t for t in pickup_tasks if str(data.route_card_id) in t.get("description", "")]
    assert len(new_pickup_tasks) > 0, "No pickup task created after material preparation"
    
    data.tasks["material_pickup"] = new_pickup_tasks[0]["id"]
    print(f"✅ Material pickup task created with ID: {data.tasks['material_pickup']}")


async def _step_5_material_pickup(client: TestClient, data: WorkflowTestData, db):
    """Step 5: Expediter picks up materials"""
    print("🚚 Step 5: Expediter picking up materials...")
    
    task_id = data.tasks["material_pickup"]
    
    # Confirm material pickup
    response = await client.post(f"/api/v1/material-pickup/pickup-tasks/{task_id}/confirm")
    assert response.status_code == 200, f"Failed to confirm material pickup: {response.text}"
    
    completed_task = response.json()
    assert completed_task["status"] == "completed", f"Expected completed status, got {completed_task['status']}"
    
    print("✅ Material pickup completed")
    
    # Verify delivery task was created
    delivery_tasks_response = await client.get("/api/v1/material-delivery/delivery-tasks")
    assert delivery_tasks_response.status_code == 200
    delivery_tasks = delivery_tasks_response.json()
    
    new_delivery_tasks = [t for t in delivery_tasks if str(data.route_card_id) in t.get("description", "")]
    assert len(new_delivery_tasks) > 0, "No delivery task created after pickup"
    
    data.tasks["material_delivery"] = new_delivery_tasks[0]["id"]
    print(f"✅ Material delivery task created with ID: {data.tasks['material_delivery']}")


async def _step_6_delivery_to_subcontractor(client: TestClient, data: WorkflowTestData, db):
    """Step 6: Deliver materials to subcontractor"""
    print("🏭 Step 6: Delivering materials to subcontractor...")
    
    task_id = data.tasks["material_delivery"]
    estimated_completion = datetime.now() + timedelta(days=3)
    
    # Confirm delivery to subcontractor
    delivery_data = {
        "estimated_completion_date": estimated_completion.isoformat(),
        "notes": "Materials delivered to ABC Machining subcontractor"
    }
    
    response = await client.post(
        f"/api/v1/material-delivery/delivery-tasks/{task_id}/confirm",
        json=delivery_data
    )
    assert response.status_code == 200, f"Failed to confirm delivery: {response.text}"
    
    completed_task = response.json()
    assert completed_task["status"] == "completed", f"Expected completed status, got {completed_task['status']}"
    
    print("✅ Material delivery to subcontractor completed")
    
    # Verify follow-up task was created
    followup_tasks_response = await client.get("/api/v1/production-followup/followup-tasks")
    assert followup_tasks_response.status_code == 200
    followup_tasks = followup_tasks_response.json()
    
    new_followup_tasks = [t for t in followup_tasks if str(data.route_card_id) in t.get("description", "")]
    assert len(new_followup_tasks) > 0, "No follow-up task created after delivery"
    
    data.tasks["production_followup"] = new_followup_tasks[0]["id"]
    print(f"✅ Production follow-up task created with ID: {data.tasks['production_followup']}")


async def _step_7_production_followup(client: TestClient, data: WorkflowTestData, db):
    """Step 7: Log production follow-up"""
    print("📞 Step 7: Logging production follow-up...")
    
    task_id = data.tasks["production_followup"]
    
    # Log follow-up as on schedule
    followup_data = {
        "status": "on_schedule",
        "notes": "Production is progressing as planned. Machining 70% complete."
    }
    
    response = await client.post(
        f"/api/v1/production-followup/followup-tasks/{task_id}",
        json=followup_data
    )
    assert response.status_code == 200, f"Failed to log follow-up: {response.text}"
    
    print("✅ Production follow-up logged")
    
    # Later, simulate production completion
    completion_data = {
        "status": "ready_for_pickup",
        "notes": "Production completed. Ready for pickup from subcontractor."
    }
    
    response = await client.post(
        f"/api/v1/production-followup/followup-tasks/{task_id}",
        json=completion_data
    )
    assert response.status_code == 200, f"Failed to log completion: {response.text}"
    
    print("✅ Production completion logged")
    
    # Verify pickup task was created
    part_pickup_tasks_response = await client.get("/api/v1/part-pickup/pickup-tasks")
    assert part_pickup_tasks_response.status_code == 200
    part_pickup_tasks = part_pickup_tasks_response.json()
    
    new_part_pickup_tasks = [t for t in part_pickup_tasks if str(data.route_card_id) in t.get("description", "")]
    assert len(new_part_pickup_tasks) > 0, "No part pickup task created"
    
    data.tasks["part_pickup"] = new_part_pickup_tasks[0]["id"]
    print(f"✅ Part pickup task created with ID: {data.tasks['part_pickup']}")


async def _step_8_part_pickup(client: TestClient, data: WorkflowTestData, db):
    """Step 8: Pick up completed parts from subcontractor"""
    print("📦 Step 8: Picking up completed parts...")
    
    task_id = data.tasks["part_pickup"]
    
    # Upload mock invoice first
    mock_invoice_data = {
        "invoice_url": "/api/v1/static/invoices/mock_invoice.pdf",
        "original_filename": "invoice_abc_machining.pdf",
        "stored_filename": "20250802_123456_uuid_invoice.pdf",
        "file_size": 15420
    }
    
    # Confirm part pickup
    pickup_data = {
        "quantity_received": 10,
        "invoice_url": mock_invoice_data["invoice_url"],
        "notes": "All parts received in good condition"
    }
    
    response = await client.post(
        f"/api/v1/part-pickup/pickup-tasks/{task_id}/confirm",
        json=pickup_data
    )
    assert response.status_code == 200, f"Failed to confirm part pickup: {response.text}"
    
    completed_task = response.json()
    assert completed_task["status"] == "completed", f"Expected completed status, got {completed_task['status']}"
    
    print("✅ Part pickup from subcontractor completed")
    
    # Verify QC inspection task was created
    qc_tasks_response = await client.get("/api/v1/qc/inspection-tasks")
    assert qc_tasks_response.status_code == 200
    qc_tasks = qc_tasks_response.json()
    
    new_qc_tasks = [t for t in qc_tasks if str(data.route_card_id) in t.get("description", "")]
    assert len(new_qc_tasks) > 0, "No QC inspection task created"
    
    data.tasks["qc_inspection"] = new_qc_tasks[0]["id"]
    print(f"✅ QC inspection task created with ID: {data.tasks['qc_inspection']}")


async def _step_9_qc_inspection(client: TestClient, data: WorkflowTestData, db):
    """Step 9: Perform QC inspection and approve"""
    print("🔍 Step 9: Performing QC inspection...")
    
    task_id = data.tasks["qc_inspection"]
    
    # Get route card details for QC
    route_card_response = await client.get(f"/api/v1/qc/route-cards/{data.route_card_id}/details")
    assert route_card_response.status_code == 200
    route_card_details = route_card_response.json()
    
    print(f"✅ Route card details retrieved for QC: {route_card_details['id']}")
    
    # Make QC decision - APPROVE
    qc_decision_data = {
        "decision": "approve",
        "quality_notes": "All parts meet specifications. Dimensional checks passed. Surface finish excellent.",
        "inspector_comments": "No defects found. Approved for delivery."
    }
    
    response = await client.post(
        f"/api/v1/qc/inspection-tasks/{task_id}/decision",
        json=qc_decision_data
    )
    assert response.status_code == 200, f"Failed to make QC decision: {response.text}"
    
    completed_inspection = response.json()
    assert completed_inspection["status"] == "completed", f"Expected completed status, got {completed_inspection['status']}"
    
    print("✅ QC inspection completed with APPROVE decision")
    
    # Verify route card status updated to completed
    updated_route_card_response = await client.get(f"/api/v1/route-cards/{data.route_card_id}")
    assert updated_route_card_response.status_code == 200
    updated_route_card = updated_route_card_response.json()
    
    assert updated_route_card["status"] == "completed", f"Expected completed route card, got {updated_route_card['status']}"
    
    print("✅ Route card status updated to completed")


async def _step_10_final_verification(client: TestClient, data: WorkflowTestData, db):
    """Step 10: Final verification of the entire workflow"""
    print("✅ Step 10: Final verification...")
    
    # Verify all audit logs were created
    audit_response = await client.get("/api/v1/audit/logs")
    if audit_response.status_code == 200:
        audit_logs = audit_response.json()
        workflow_logs = [log for log in audit_logs if 
                        str(data.warehouse_request_id) in str(log.get("target_id", "")) or
                        str(data.order_id) in str(log.get("target_id", "")) or
                        str(data.route_card_id) in str(log.get("target_id", ""))]
        
        assert len(workflow_logs) > 0, "No audit logs found for workflow"
        print(f"✅ {len(workflow_logs)} audit logs verified")
    
    # Verify final notifications
    notifications_response = await client.get("/api/v1/notifications/me")
    assert notifications_response.status_code == 200
    all_notifications = notifications_response.json()
    
    workflow_notifications = [n for n in all_notifications if 
                             any(keyword in n["message"].lower() for keyword in 
                                 ["warehouse request", "production order", "route card", "pickup", "delivery", "qc"])]
    
    assert len(workflow_notifications) >= 5, f"Expected at least 5 workflow notifications, got {len(workflow_notifications)}"
    print(f"✅ {len(workflow_notifications)} notifications verified")
    
    # Verify order status
    final_order_response = await client.get(f"/api/v1/orders/{data.order_id}")
    if final_order_response.status_code == 200:
        final_order = final_order_response.json()
        assert final_order["status"] in ["completed", "fulfilled"], f"Expected completed order, got {final_order['status']}"
        print(f"✅ Final order status: {final_order['status']}")
    
    # Verify warehouse request status
    final_request_response = await client.get(f"/api/v1/warehouse/warehouse-requests/{data.warehouse_request_id}")
    assert final_request_response.status_code == 200
    final_request = final_request_response.json()
    
    print(f"✅ Final warehouse request status: {final_request['status']}")
    
    print("\n🎉 COMPLETE END-TO-END WORKFLOW TEST PASSED! 🎉")
    print("=" * 60)
    print(f"📝 Warehouse Request ID: {data.warehouse_request_id}")
    print(f"🏭 Production Order ID: {data.order_id}")
    print(f"🗺️ Route Card ID: {data.route_card_id}")
    print(f"📋 Tasks Created: {len(data.tasks)}")
    print(f"🔔 Notifications: {len(workflow_notifications)}")
    print("=" * 60)
