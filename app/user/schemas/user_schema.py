from uuid import UUID
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    """
    Enum for user roles.
    """
    ADMIN = "ADMIN"
    MEMBER ="MEMBER"


class UserCreate(BaseModel):
    """
    Schema for creating a new user.
    Requires an email and password.
    Optionally accepts an avatar URL.
    """
    email: EmailStr
    password: str
    avatar_url: str | None = None


class UserResponse(BaseModel):
    """
    Schema for returning user data in API responses.
    """
    id: UUID
    email: EmailStr
    avatar_url: str | None = None
    role: UserRole
    is_active: bool
    created_at: datetime


class UserLogin(BaseModel):
    """
    Schema for user login.
    Requires an email and password.
    """
    email: EmailStr
    password: str

    class config:
        """
        Configurations for the UserResponse schema.
        """
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """
    Schema for token data.
    Contains the user ID.
    """
    sub: UUID | None = None
