from pydantic import BaseModel, EmailStr
from typing import Optional, List

class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str

class RoleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]

    class Config:
        orm_mode = True

class UserResponse(UserBase):
    id: int
    is_active: bool
    roles: List[RoleResponse]

    class Config:
        orm_mode = True
