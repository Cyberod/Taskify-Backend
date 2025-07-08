from uuid import UUID
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
import re


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
    password: str = Field(..., min_length=8, max_length=128, description="Password must be between 8 and 128 characters.")
    avatar_url: str | None = None

    @validator('email')
    def validate_email(cls, v):
        """
        validate email format
        """
        if not v or not v.strip():
            raise ValueError("Email cannot be empty")
        # check email format with regex expression
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if not re.match(email_regex, v):
            raise ValueError("Invalid email format")
        return v.lower().strip()
    
    @validator('password')
    def validate_password(cls, v):
        """
        Validate password strength.
        Password must be between 8 and 128 characters.
        """
        if not v or not v.strip():
            raise ValueError("Password cannot be empty")
        
        if len(v) < 8 or len(v) > 128:
            raise ValueError("Password must be between 8 and 128 characters.")
        return v

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
    password: str = Field(..., min_length=8, max_length=128, description="Password is required")

    @validator('email')
    def validate_email(cls, v):
        if not v or not v.strip():
            raise ValueError('Email cannot be empty')
        return v.lower().strip()

    @validator('password')
    def validate_password(cls, v):
        if not v or not v.strip():
            raise ValueError('Password cannot be empty')
        return v

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
