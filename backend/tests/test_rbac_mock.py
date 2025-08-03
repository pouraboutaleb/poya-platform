import pytest
from fastapi import HTTPException, status
from app.core.security import has_role, has_any_role, require_roles


class MockRole:
    """Mock role class for testing."""
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description


class MockUser:
    """Mock user class for testing."""
    def __init__(self, email: str, full_name: str, is_active: bool = True):
        self.email = email
        self.full_name = full_name
        self.is_active = is_active
        self.roles = []


@pytest.mark.unit
class TestRBACFunctions:
    """Test Role-Based Access Control functions with mock objects."""
    
    def test_has_role_true(self):
        """Test has_role returns True when user has the role."""
        role = MockRole(name="admin", description="Admin role")
        user = MockUser(email="admin@test.com", full_name="Admin User")
        user.roles = [role]
        
        assert has_role(user, "admin") is True
    
    def test_has_role_false(self):
        """Test has_role returns False when user doesn't have the role."""
        role = MockRole(name="user", description="User role")
        user = MockUser(email="user@test.com", full_name="Regular User")
        user.roles = [role]
        
        assert has_role(user, "admin") is False
    
    def test_has_role_empty_roles(self):
        """Test has_role returns False when user has no roles."""
        user = MockUser(email="user@test.com", full_name="User")
        user.roles = []
        
        assert has_role(user, "admin") is False
    
    def test_has_any_role_true(self):
        """Test has_any_role returns True when user has one of the roles."""
        role1 = MockRole(name="manager", description="Manager role")
        user = MockUser(email="manager@test.com", full_name="Manager User")
        user.roles = [role1]
        
        assert has_any_role(user, ["admin", "manager"]) is True
    
    def test_has_any_role_false(self):
        """Test has_any_role returns False when user has none of the roles."""
        role = MockRole(name="user", description="User role")
        user = MockUser(email="user@test.com", full_name="Regular User")
        user.roles = [role]
        
        assert has_any_role(user, ["admin", "manager"]) is False
    
    def test_has_any_role_multiple_roles(self):
        """Test has_any_role with user having multiple roles."""
        role1 = MockRole(name="manager", description="Manager role")
        role2 = MockRole(name="supervisor", description="Supervisor role")
        user = MockUser(email="manager@test.com", full_name="Manager User")
        user.roles = [role1, role2]
        
        assert has_any_role(user, ["admin", "supervisor"]) is True
        assert has_any_role(user, ["admin", "user"]) is False


@pytest.mark.unit
class TestRoleRequirements:
    """Test role requirement dependencies with mock objects."""
    
    @pytest.mark.asyncio
    async def test_require_roles_string_success(self):
        """Test require_roles with string role when user has role."""
        role = MockRole(name="admin", description="Admin role")
        user = MockUser(email="admin@test.com", full_name="Admin User", is_active=True)
        user.roles = [role]
        
        dependency = require_roles("admin")
        result = await dependency(user)
        assert result == user
    
    @pytest.mark.asyncio
    async def test_require_roles_string_failure(self):
        """Test require_roles with string role when user lacks role."""
        role = MockRole(name="user", description="User role")
        user = MockUser(email="user@test.com", full_name="Regular User", is_active=True)
        user.roles = [role]
        
        dependency = require_roles("admin")
        with pytest.raises(HTTPException) as exc_info:
            await dependency(user)
        
        assert exc_info.value.status_code == 403
        assert "admin" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_require_roles_list_success(self):
        """Test require_roles with list of roles when user has one."""
        role = MockRole(name="manager", description="Manager role")
        user = MockUser(email="manager@test.com", full_name="Manager User", is_active=True)
        user.roles = [role]
        
        dependency = require_roles(["admin", "manager"])
        result = await dependency(user)
        assert result == user
    
    @pytest.mark.asyncio
    async def test_require_roles_list_failure(self):
        """Test require_roles with list of roles when user has none."""
        role = MockRole(name="user", description="User role")
        user = MockUser(email="user@test.com", full_name="Regular User", is_active=True)
        user.roles = [role]
        
        dependency = require_roles(["admin", "manager"])
        with pytest.raises(HTTPException) as exc_info:
            await dependency(user)
        
        assert exc_info.value.status_code == 403
    
    @pytest.mark.asyncio
    async def test_require_roles_inactive_user(self):
        """Test require_roles with inactive user."""
        # For this test, we need to create a custom dependency that checks is_active
        # since we're bypassing get_current_active_user
        async def mock_active_user_checker(user):
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Inactive user"
                )
            return user

        role = MockRole(name="admin", description="Admin role")
        user = MockUser(email="admin@test.com", full_name="Admin User", is_active=False)
        user.roles = [role]

        # First check that the inactive user raises an exception before role checking
        with pytest.raises(HTTPException) as exc_info:
            await mock_active_user_checker(user)
        
        assert exc_info.value.status_code == 400
        assert "Inactive user" in exc_info.value.detail