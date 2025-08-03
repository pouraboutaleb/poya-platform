from datetime import datetime, timedelta
from typing import Optional, List, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from .config import settings
from ..db.session import get_db
from ..models.user import User

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email address"""
    return db.query(User).filter(User.email == email).first()

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate a user with email and password"""
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = get_user_by_email(db, email)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user = Depends(get_current_user)):
    """Get current active user - depends on get_current_user and checks if user is active"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

# Role-based access control functions
def has_role(user: User, role_name: str) -> bool:
    """Check if user has a specific role"""
    return any(role.name == role_name for role in user.roles)

def has_any_role(user: User, role_names: List[str]) -> bool:
    """Check if user has any of the specified roles"""
    user_role_names = {role.name for role in user.roles}
    return bool(user_role_names.intersection(set(role_names)))

def require_roles(required_roles: Union[str, List[str]]):
    """
    Dependency factory for requiring specific roles.
    Can accept a single role string or a list of roles (user needs ANY of them).
    """
    if isinstance(required_roles, str):
        required_roles = [required_roles]
    
    async def role_checker(current_user: User = Depends(get_current_active_user)):
        if not has_any_role(current_user, required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(required_roles)}"
            )
        return current_user
    return role_checker

def require_all_roles(required_roles: List[str]):
    """
    Dependency factory for requiring ALL specified roles.
    User must have all the roles listed.
    """
    async def role_checker(current_user: User = Depends(get_current_active_user)):
        user_role_names = {role.name for role in current_user.roles}
        missing_roles = set(required_roles) - user_role_names
        if missing_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Missing required roles: {', '.join(missing_roles)}"
            )
        return current_user
    return role_checker

# Specific role dependencies for common use cases
require_admin = require_roles("admin")
require_manager = require_roles(["manager", "admin"])
require_production_manager = require_roles(["production_manager", "manager", "admin"])
require_warehouse_staff = require_roles(["warehouse_staff", "manager", "admin"])
require_quality_control = require_roles(["quality_control", "manager", "admin"])
require_supervisor = require_roles(["supervisor", "manager", "admin"])

def check_permissions(required_roles: list[str]):
    async def role_checker(current_user = Depends(get_current_user)):
        for role in current_user.roles:
            if role.name in required_roles:
                return True
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have the required permissions"
        )
    return role_checker
