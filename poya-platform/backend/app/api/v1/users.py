from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..core.security import get_current_user, get_password_hash, check_permissions
from ..schemas.user import UserCreate, UserResponse
from ..models.user import User
from ..db.session import get_db

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register_user(
    user_create: UserCreate,
    db: Session = Depends(get_db)
):
    # Check if user already exists
    if db.query(User).filter(User.email == user_create.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    db_user = User(
        email=user_create.email,
        full_name=user_create.full_name,
        hashed_password=get_password_hash(user_create.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user = Depends(get_current_user)):
    return current_user

@router.get("/", response_model=List[UserResponse])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: bool = Depends(check_permissions(["admin"]))
):
    users = db.query(User).offset(skip).limit(limit).all()
    return users
