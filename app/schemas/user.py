from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime

class UserBase(BaseModel):
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = True

# Properties to receive via API on creation   
class UserCreate(UserBase):
    email: EmailStr
    password: str

    @field_validator('password')
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isalpha() for char in v):
            raise ValueError('Password must contain at least one letter')
        return v

# Properties to receive via API on update    
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


    @field_validator('password')
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isalpha() for char in v):
            raise ValueError('Password must contain at least one letter')
        return v

# Properties shared by models stored in DB
class UserInDBBase(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Properties to return via API
class User(UserInDBBase):
    pass

# Properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str