import pytest
from fastapi import HTTPException, status

from app.core.security import has_role, has_any_role, require_roles
from app.models.user import User, Role


class TestRBACWithModels:
    """Test RBAC functions with actual SQLAlchemy models (basic instantiation only)."""
    
    def test_model_instantiation(self):
        """Test that models can be instantiated without database."""
        # These should work without hitting the database
        role = Role()
        role.name = "admin"
        role.description = "Admin role"
        
        user = User()
        user.email = "admin@test.com"
        user.full_name = "Admin User"
        user.is_active = True
        user.roles = [role]
        
        # Test RBAC functions
        assert has_role(user, "admin") == True
        assert has_role(user, "user") == False
        assert has_any_role(user, ["admin", "user"]) == True
        assert has_any_role(user, ["manager", "user"]) == False
    
    def test_empty_roles(self):
        """Test user with no roles."""
        user = User()
        user.email = "user@test.com"
        user.full_name = "User"
        user.is_active = True
        user.roles = []
        
        assert has_role(user, "admin") == False
        assert has_any_role(user, ["admin", "user"]) == False
    
    def test_multiple_roles(self):
        """Test user with multiple roles."""
        role1 = Role()
        role1.name = "manager"
        role1.description = "Manager role"
        
        role2 = Role()
        role2.name = "user"
        role2.description = "User role"
        
        user = User()
        user.email = "manager@test.com"
        user.full_name = "Manager User"
        user.is_active = True
        user.roles = [role1, role2]
        
        assert has_role(user, "manager") == True
        assert has_role(user, "user") == True
        assert has_role(user, "admin") == False
        assert has_any_role(user, ["admin", "manager"]) == True
        assert has_any_role(user, ["admin", "editor"]) == False
