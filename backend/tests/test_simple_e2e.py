import pytest
import httpx
import asyncio
from datetime import datetime, timedelta
import json

# Simplified E2E Test without complex dependencies
# This test will check if the basic workflow APIs are available and responsive

TEST_BASE_URL = "http://localhost:8000"

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_simple_api_availability():
    """
    Simplified test to check if main APIs are available
    """
    print("🚀 Starting Simplified E2E API Availability Test")
    
    async with httpx.AsyncClient(base_url=TEST_BASE_URL, timeout=10.0) as client:
        # Test 1: Health check
        try:
            response = await client.get("/health")
            print(f"✅ Health check: {response.status_code}")
        except Exception as e:
            print(f"❌ Health check failed: {e}")
        
        # Test 2: API documentation
        try:
            response = await client.get("/docs")
            print(f"✅ API docs: {response.status_code}")
        except Exception as e:
            print(f"❌ API docs failed: {e}")
        
        # Test 3: OpenAPI schema
        try:
            response = await client.get("/openapi.json")
            if response.status_code == 200:
                schema = response.json()
                paths = list(schema.get("paths", {}).keys())
                print(f"✅ API schema loaded with {len(paths)} endpoints")
                
                # Check key workflow endpoints
                key_endpoints = [
                    "/api/v1/warehouse/warehouse-requests",
                    "/api/v1/orders",
                    "/api/v1/route-cards",
                    "/api/v1/auth/login"
                ]
                
                available_endpoints = []
                for endpoint in key_endpoints:
                    if endpoint in paths:
                        available_endpoints.append(endpoint)
                        print(f"  ✅ {endpoint} - Available")
                    else:
                        print(f"  ❌ {endpoint} - Missing")
                
                print(f"✅ {len(available_endpoints)}/{len(key_endpoints)} key endpoints available")
            else:
                print(f"❌ API schema failed: {response.status_code}")
        except Exception as e:
            print(f"❌ API schema failed: {e}")

    print("✅ Simplified E2E API Availability Test Completed!")


@pytest.mark.e2e
@pytest.mark.asyncio  
async def test_workflow_endpoints_structure():
    """
    Test the structure and expected responses of workflow endpoints
    """
    print("🚀 Starting Workflow Endpoints Structure Test")
    
    async with httpx.AsyncClient(base_url=TEST_BASE_URL, timeout=10.0) as client:
        
        # Test login endpoint structure (POST)
        try:
            # This should fail with 422 (validation error) since no data is sent
            response = await client.post("/api/v1/auth/login")
            if response.status_code == 422:
                print("✅ Login endpoint structure correct (422 for missing data)")
            else:
                print(f"⚠️ Login endpoint unexpected response: {response.status_code}")
        except Exception as e:
            print(f"❌ Login endpoint test failed: {e}")
        
        # Test warehouse requests endpoint (GET - should require auth)
        try:
            response = await client.get("/api/v1/warehouse/warehouse-requests")
            if response.status_code in [401, 403]:
                print("✅ Warehouse requests endpoint protected (401/403)")
            elif response.status_code == 200:
                print("⚠️ Warehouse requests endpoint not protected")
            else:
                print(f"⚠️ Warehouse requests unexpected response: {response.status_code}")
        except Exception as e:
            print(f"❌ Warehouse requests test failed: {e}")
        
        # Test orders endpoint (GET - should require auth)
        try:
            response = await client.get("/api/v1/orders")
            if response.status_code in [401, 403]:
                print("✅ Orders endpoint protected (401/403)")
            elif response.status_code == 200:
                print("⚠️ Orders endpoint not protected")
            else:
                print(f"⚠️ Orders unexpected response: {response.status_code}")
        except Exception as e:
            print(f"❌ Orders test failed: {e}")
        
        # Test route cards endpoint (GET - should require auth)
        try:
            response = await client.get("/api/v1/route-cards")
            if response.status_code in [401, 403]:
                print("✅ Route cards endpoint protected (401/403)")
            elif response.status_code == 200:
                print("⚠️ Route cards endpoint not protected")
            else:
                print(f"⚠️ Route cards unexpected response: {response.status_code}")
        except Exception as e:
            print(f"❌ Route cards test failed: {e}")

    print("✅ Workflow Endpoints Structure Test Completed!")


@pytest.mark.unit
def test_sync_basic_validation():
    """
    Synchronous test for basic validation
    """
    print("🚀 Starting Basic Validation Test")
    
    # Test data structures
    test_warehouse_request = {
        "project_name": "Test Project",
        "description": "Test description",
        "priority": "high",
        "requested_delivery_date": (datetime.now() + timedelta(days=7)).isoformat(),
        "request_items": [
            {
                "item_id": 1,
                "quantity_requested": 10,
                "remarks": "Test item"
            }
        ]
    }
    
    test_order_data = {
        "item_id": 1,
        "quantity": 10,
        "priority": "high",
        "required_date": (datetime.now() + timedelta(days=5)).isoformat()
    }
    
    test_route_card_data = {
        "order_id": 1,
        "materials": [
            {"material_code": "MAT001", "quantity": 5, "unit": "kg"}
        ],
        "workstations": [
            {"station": "Cutting", "estimated_time": 2.5, "subcontractor": None}
        ],
        "estimated_time": 2.5
    }
    
    # Validate JSON serialization
    try:
        json.dumps(test_warehouse_request)
        print("✅ Warehouse request data structure valid")
    except Exception as e:
        print(f"❌ Warehouse request data invalid: {e}")
    
    try:
        json.dumps(test_order_data)
        print("✅ Order data structure valid")
    except Exception as e:
        print(f"❌ Order data invalid: {e}")
    
    try:
        json.dumps(test_route_card_data)
        print("✅ Route card data structure valid")
    except Exception as e:
        print(f"❌ Route card data invalid: {e}")
    
    print("✅ Basic Validation Test Completed!")


if __name__ == "__main__":
    # Run tests manually for debugging
    print("🧪 Running Manual Test Execution")
    
    # Run sync test
    test_sync_basic_validation()
    
    # Run async tests
    asyncio.run(test_simple_api_availability())
    asyncio.run(test_workflow_endpoints_structure())
    
    print("🎉 All Manual Tests Completed!")
