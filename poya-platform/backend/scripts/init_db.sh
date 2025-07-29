#!/bin/bash

# Create database if it doesn't exist
PGPASSWORD=postgres psql -U postgres -h localhost -tc "SELECT 1 FROM pg_database WHERE datname = 'poya_db'" | grep -q 1 || PGPASSWORD=postgres psql -U postgres -h localhost -c "CREATE DATABASE poya_db"

# Run migrations
cd /workspaces/MRDPOL/poya-platform/backend
alembic upgrade head

# Create admin user if it doesn't exist
python3 << END
from app.db.session import SessionLocal
from app.models.user import User, Role
from app.core.security import get_password_hash

db = SessionLocal()

# Check if admin user exists
admin_email = "admin@poya.com"
admin_user = db.query(User).filter(User.email == admin_email).first()

if not admin_user:
    # Get admin role
    admin_role = db.query(Role).filter(Role.name == "admin").first()
    
    # Create admin user
    admin_user = User(
        email=admin_email,
        full_name="System Administrator",
        hashed_password=get_password_hash("admin123"),  # Change this in production!
        is_active=True
    )
    admin_user.roles.append(admin_role)
    
    db.add(admin_user)
    db.commit()
    print("Admin user created successfully!")
else:
    print("Admin user already exists!")

db.close()
END
