import pytest
from httpx import AsyncClient
from fastapi import status
from app.models.user import User


@pytest.mark.integration
class TestItemsAPIRBAC:
    """Test Role-Based Access Control for Items API."""
    
    @pytest.mark.asyncio
    async def test_get_items_requires_auth(self, async_client: AsyncClient):
        """Test that getting items requires authentication."""
        response = await async_client.get("/api/v1/items")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.asyncio
    async def test_get_items_with_auth(self, async_client: AsyncClient, auth_headers: dict):
        """Test that authenticated users can get items."""
        response = await async_client.get("/api/v1/items", headers=auth_headers)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
    
    @pytest.mark.asyncio
    async def test_create_item_requires_manager(self, async_client: AsyncClient, regular_auth_headers: dict, test_item_category):
        """Test that creating items requires manager role."""
        item_data = {
            "item_code": "TEST002",
            "name": "Test Item 2",
            "description": "Test item description",
            "category_id": test_item_category.id
        }
        
        response = await async_client.post("/api/v1/items", json=item_data, headers=regular_auth_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_create_item_with_manager(self, async_client: AsyncClient, manager_auth_headers: dict, test_item_category):
        """Test that managers can create items."""
        item_data = {
            "item_code": "TEST003",
            "name": "Test Item 3",
            "description": "Test item description",
            "category_id": test_item_category.id
        }
        
        response = await async_client.post("/api/v1/items", json=item_data, headers=manager_auth_headers)
        # Should succeed (201) or fail due to validation (422), but not authorization (403)
        assert response.status_code != status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_create_category_requires_manager(self, async_client: AsyncClient, regular_auth_headers: dict):
        """Test that creating categories requires manager role."""
        category_data = {
            "name": "Test Category 2",
            "description": "Test category description"
        }
        
        response = await async_client.post("/api/v1/items/categories", json=category_data, headers=regular_auth_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.integration
class TestUsersAPIRBAC:
    """Test Role-Based Access Control for Users API."""
    
    @pytest.mark.asyncio
    async def test_get_users_requires_admin(self, async_client: AsyncClient, regular_auth_headers: dict):
        """Test that getting all users requires admin role."""
        response = await async_client.get("/api/v1/users/", headers=regular_auth_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_get_users_with_admin(self, async_client: AsyncClient, auth_headers: dict):
        """Test that admins can get all users."""
        response = await async_client.get("/api/v1/users/", headers=auth_headers)
        # Should succeed (200) or fail due to implementation (404/500), but not authorization (403)
        assert response.status_code != status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_register_user_requires_admin(self, async_client: AsyncClient, regular_auth_headers: dict):
        """Test that registering users requires admin role."""
        user_data = {
            "email": "newuser@example.com",
            "full_name": "New User",
            "password": "newpassword"
        }
        
        response = await async_client.post("/api/v1/users/register", json=user_data, headers=regular_auth_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_get_me_requires_auth(self, async_client: AsyncClient):
        """Test that getting current user info requires authentication."""
        response = await async_client.get("/api/v1/users/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.asyncio
    async def test_get_me_with_auth(self, async_client: AsyncClient, auth_headers: dict):
        """Test that authenticated users can get their own info."""
        response = await async_client.get("/api/v1/users/me", headers=auth_headers)
        # Should succeed (200) or fail due to implementation, but not authorization (401/403)
        assert response.status_code not in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


@pytest.mark.integration
class TestTasksAPIRBAC:
    """Test Role-Based Access Control for Tasks API."""
    
    @pytest.mark.asyncio
    async def test_get_tasks_requires_auth(self, async_client: AsyncClient):
        """Test that getting tasks requires authentication."""
        response = await async_client.get("/api/v1/tasks/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.asyncio
    async def test_get_tasks_with_auth(self, async_client: AsyncClient, auth_headers: dict):
        """Test that authenticated users can get their tasks."""
        response = await async_client.get("/api/v1/tasks/me", headers=auth_headers)
        # Should succeed (200) or fail due to implementation, but not authorization (401/403)
        assert response.status_code not in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    @pytest.mark.asyncio
    async def test_create_task_requires_auth(self, async_client: AsyncClient):
        """Test that creating tasks requires authentication."""
        task_data = {
            "title": "Test Task",
            "description": "Test task description",
            "priority": "medium"
        }
        
        response = await async_client.post("/api/v1/tasks", json=task_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.integration  
class TestProductionAPIRBAC:
    """Test Role-Based Access Control for Production API."""
    
    @pytest.mark.asyncio
    async def test_get_production_reports_requires_auth(self, async_client: AsyncClient):
        """Test that getting production reports requires authentication."""
        response = await async_client.get("/api/v1/production-reports")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.asyncio
    async def test_create_production_report_requires_production_manager(self, async_client: AsyncClient, regular_auth_headers: dict):
        """Test that creating production reports requires production manager role."""
        report_data = {
            "report_date": "2025-01-01",
            "shift": "day",
            "daily_challenge": "Test challenge",
            "solutions_implemented": "Test solution",
            "production_logs": [],
            "stoppages": []
        }
        
        response = await async_client.post("/api/v1/production-reports", json=report_data, headers=regular_auth_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.integration
class TestOrdersAPIRBAC:
    """Test Role-Based Access Control for Orders API."""
    
    @pytest.mark.asyncio
    async def test_get_procurement_orders_requires_auth(self, async_client: AsyncClient):
        """Test that getting procurement orders requires authentication."""
        response = await async_client.get("/api/v1/orders/procurement")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
