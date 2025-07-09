from pydantic import BaseModel, EmailStr, Field

class EmailVerificationRequest(BaseModel):
    email: EmailStr


class EmailVerificationConfirm(BaseModel):
    email: EmailStr
    otp: str = Field(
        ...,
        min_length=6,
        max_length=6,
        description="6 digit verification code"
    )

class ResendVerificationRequest(BaseModel):
    email: EmailStr