#!/bin/bash

# Initialize user roles in the database
# This script should be run after the database is created and migrated

echo "Initializing user roles..."

# Create a Python script to initialize roles
python3 << 'EOF'
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.core.config import settings
from app.services.user_role_service import UserRoleService
from app.models.user import User, Role

def init_roles():
    """Initialize default roles in the database"""
    try:
        engine = create_engine(settings.database_url)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        user_role_service = UserRoleService(db)
        user_role_service.ensure_default_roles_exist()
        
        print("✅ Default roles initialized successfully!")
        
        # Create a default admin user if it doesn't exist
        admin_user = db.query(User).filter(User.email == "admin@mrdpol.com").first()
        if not admin_user:
            from app.core.security import get_password_hash
            admin_user = User(
                email="admin@mrdpol.com",
                full_name="System Administrator",
                hashed_password=get_password_hash("admin123"),
                is_active=True,
                is_warehouse_staff=True
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            
            # Assign admin role
            user_role_service.assign_role_to_user(admin_user.id, "admin")
            user_role_service.assign_role_to_user(admin_user.id, "warehouse_manager")
            
            print("✅ Default admin user created (admin@mrdpol.com / admin123)")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error initializing roles: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = init_roles()
    sys.exit(0 if success else 1)

EOF

echo "Role initialization completed!"
