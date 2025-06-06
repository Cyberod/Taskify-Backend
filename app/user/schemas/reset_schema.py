from pydantic import BaseModel, EmailStr, Field

class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6, description="One-time password sent to the user's email")
    new_password: str = Field(..., min_length=8, description="New password for the user")