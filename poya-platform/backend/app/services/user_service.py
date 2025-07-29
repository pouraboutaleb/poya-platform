from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional

from ..models.user import User, Role
from ..schemas.user import UserCreate
from ..core.security import get_password_hash

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_default_role(db: Session) -> Role:
    return db.query(Role).filter(Role.name == "user").first()

def create_user(db: Session, user_data: UserCreate) -> User:
    # Check if user exists
    if get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Get default role
    default_role = get_default_role(db)
    if not default_role:
        # Create default role if it doesn't exist
        default_role = Role(name="user", description="Regular user")
        db.add(default_role)
        db.commit()
        db.refresh(default_role)
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        is_active=True
    )
    
    # Add default role
    db_user.roles.append(default_role)
    
    # Save to database
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user
