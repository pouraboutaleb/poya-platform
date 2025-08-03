"""Token schemas for authentication"""
from pydantic import BaseModel


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Token data schema"""
    username: str | None = None
    user_id: int | None = None


class RefreshToken(BaseModel):
    """Refresh token schema"""
    refresh_token: str
