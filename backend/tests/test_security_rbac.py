import pytest
from fastapi import HTTPException
from app.core.security import has_role, has_any_role, require_roles, require_admin
from app.models.user import User, Role


class TestRBACFunctions:
    """Test Role-Based Access Control functions."""
    
    def test_has_role_true(self):
        """Test has_role returns True when user has the role."""
        role = Role(name="admin", description="Admin role")
        user = User(email="admin@test.com", full_name="Admin User")
        user.roles = [role]
        
        assert has_role(user, "admin") is True
    
    def test_has_role_false(self):
        """Test has_role returns False when user doesn't have the role."""
        role = Role(name="user", description="User role")
        user = User(email="user@test.com", full_name="Regular User")
        user.roles = [role]
        
        assert has_role(user, "admin") is False
    
    def test_has_role_empty_roles(self):
        """Test has_role returns False when user has no roles."""
        user = User(email="user@test.com", full_name="User")
        user.roles = []
        
        assert has_role(user, "admin") is False
    
    def test_has_any_role_true(self):
        """Test has_any_role returns True when user has one of the roles."""
        role1 = Role(name="manager", description="Manager role")
        role2 = Role(name="admin", description="Admin role")
        user = User(email="manager@test.com", full_name="Manager User")
        user.roles = [role1]
        
        assert has_any_role(user, ["admin", "manager"]) is True
    
    def test_has_any_role_false(self):
        """Test has_any_role returns False when user has none of the roles."""
        role = Role(name="user", description="User role")
        user = User(email="user@test.com", full_name="Regular User")
        user.roles = [role]
        
        assert has_any_role(user, ["admin", "manager"]) is False
    
    def test_has_any_role_multiple_roles(self):
        """Test has_any_role with user having multiple roles."""
        role1 = Role(name="manager", description="Manager role")
        role2 = Role(name="supervisor", description="Supervisor role")
        user = User(email="manager@test.com", full_name="Manager User")
        user.roles = [role1, role2]
        
        assert has_any_role(user, ["admin", "supervisor"]) is True
        assert has_any_role(user, ["admin", "user"]) is False


@pytest.mark.unit
class TestRoleRequirements:
    """Test role requirement dependencies."""
    
    @pytest.mark.asyncio
    async def test_require_roles_string_success(self):
        """Test require_roles with string role when user has role."""
        role = Role(name="admin", description="Admin role")
        user = User(email="admin@test.com", full_name="Admin User", is_active=True)
        user.roles = [role]
        
        dependency = require_roles("admin")
        result = await dependency(user)
        assert result == user
    
    @pytest.mark.asyncio
    async def test_require_roles_string_failure(self):
        """Test require_roles with string role when user lacks role."""
        role = Role(name="user", description="User role")
        user = User(email="user@test.com", full_name="Regular User", is_active=True)
        user.roles = [role]
        
        dependency = require_roles("admin")
        with pytest.raises(HTTPException) as exc_info:
            await dependency(user)
        
        assert exc_info.value.status_code == 403
        assert "admin" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_require_roles_list_success(self):
        """Test require_roles with list of roles when user has one."""
        role = Role(name="manager", description="Manager role")
        user = User(email="manager@test.com", full_name="Manager User", is_active=True)
        user.roles = [role]
        
        dependency = require_roles(["admin", "manager"])
        result = await dependency(user)
        assert result == user
    
    @pytest.mark.asyncio
    async def test_require_roles_list_failure(self):
        """Test require_roles with list of roles when user has none."""
        role = Role(name="user", description="User role")
        user = User(email="user@test.com", full_name="Regular User", is_active=True)
        user.roles = [role]
        
        dependency = require_roles(["admin", "manager"])
        with pytest.raises(HTTPException) as exc_info:
            await dependency(user)
        
        assert exc_info.value.status_code == 403
    
    @pytest.mark.asyncio
    async def test_require_admin_success(self):
        """Test require_admin when user has admin role."""
        role = Role(name="admin", description="Admin role")
        user = User(email="admin@test.com", full_name="Admin User", is_active=True)
        user.roles = [role]
        
        result = await require_admin(user)
        assert result == user
    
    @pytest.mark.asyncio
    async def test_require_admin_failure(self):
        """Test require_admin when user lacks admin role."""
        role = Role(name="user", description="User role")
        user = User(email="user@test.com", full_name="Regular User", is_active=True)
        user.roles = [role]
        
        with pytest.raises(HTTPException) as exc_info:
            await require_admin(user)
        
        assert exc_info.value.status_code == 403
