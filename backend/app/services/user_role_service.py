from typing import Optional, List
from sqlalchemy.orm import Session
from ..models.user import User, Role


class UserRoleService:
    """Service for managing user roles and finding users by their roles"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_role(self, role_name: str) -> Optional[User]:
        """
        Get the first user with a specific role
        
        Args:
            role_name: The name of the role to search for
            
        Returns:
            Optional[User]: The first user with the specified role, or None if not found
        """
        return (
            self.db.query(User)
            .join(User.roles)
            .filter(Role.name == role_name)
            .first()
        )
    
    def get_users_by_role(self, role_name: str) -> List[User]:
        """
        Get all users with a specific role
        
        Args:
            role_name: The name of the role to search for
            
        Returns:
            List[User]: List of users with the specified role
        """
        return (
            self.db.query(User)
            .join(User.roles)
            .filter(Role.name == role_name)
            .all()
        )
    
    def get_warehouse_manager(self) -> Optional[User]:
        """Get the warehouse manager user"""
        # First try to find a specific warehouse manager role
        user = self.get_user_by_role("warehouse_manager")
        if user:
            return user
        
        # Fallback to general manager role with warehouse staff flag
        return (
            self.db.query(User)
            .join(User.roles)
            .filter(Role.name == "manager", User.is_warehouse_staff == True)
            .first()
        )
    
    def get_warehouse_staff(self) -> Optional[User]:
        """Get any warehouse staff member"""
        return (
            self.db.query(User)
            .filter(User.is_warehouse_staff == True)
            .first()
        )
    
    def get_purchasing_manager(self) -> Optional[User]:
        """Get the purchasing manager user"""
        # First try to find a specific purchasing manager role
        user = self.get_user_by_role("purchasing_manager")
        if user:
            return user
        
        # Fallback to general manager role
        return self.get_user_by_role("manager")
    
    def get_procurement_team_lead(self) -> Optional[User]:
        """Get the procurement team lead user"""
        # First try to find a specific procurement lead role
        user = self.get_user_by_role("procurement_lead")
        if user:
            return user
        
        # Fallback to purchasing manager
        return self.get_purchasing_manager()
    
    def get_production_planner(self) -> Optional[User]:
        """Get the production planner user"""
        # First try to find a specific production planner role
        user = self.get_user_by_role("production_planner")
        if user:
            return user
        
        # Fallback to production manager
        return self.get_user_by_role("production_manager")
    
    def get_managers(self) -> List[User]:
        """Get all users with manager roles"""
        manager_roles = [
            "manager", "warehouse_manager", "purchasing_manager", 
            "production_manager", "qc_manager", "admin"
        ]
        
        users = []
        for role in manager_roles:
            users.extend(self.get_users_by_role(role))
        
        # Remove duplicates
        return list(set(users))
    
    def ensure_default_roles_exist(self):
        """Ensure default roles exist in the database"""
        default_roles = [
            ("admin", "System administrator"),
            ("manager", "General manager"),
            ("warehouse_manager", "Warehouse manager"),
            ("warehouse_staff", "Warehouse staff member"),
            ("purchasing_manager", "Purchasing manager"),
            ("procurement_lead", "Procurement team lead"),
            ("production_manager", "Production manager"),
            ("production_planner", "Production planner"),
            ("qc_manager", "Quality control manager"),
            ("qc_inspector", "Quality control inspector"),
            ("user", "Regular user")
        ]
        
        for role_name, description in default_roles:
            existing_role = self.db.query(Role).filter(Role.name == role_name).first()
            if not existing_role:
                new_role = Role(name=role_name, description=description)
                self.db.add(new_role)
        
        self.db.commit()
    
    def assign_role_to_user(self, user_id: int, role_name: str) -> bool:
        """
        Assign a role to a user
        
        Args:
            user_id: The ID of the user
            role_name: The name of the role to assign
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            role = self.db.query(Role).filter(Role.name == role_name).first()
            
            if user and role and role not in user.roles:
                user.roles.append(role)
                self.db.commit()
                return True
            return False
        except Exception:
            self.db.rollback()
            return False
