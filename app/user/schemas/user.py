from uuid import UUID
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    """
    Enum for user roles.
    """
    ADMIN = "admin"
    MEMBER ="member"


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

class config:
    """
    Configurations for the UserResponse schema.
    """
    from_attributes = True
