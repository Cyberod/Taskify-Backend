from pydantic import BaseModel, Field, validator
from uuid import UUID



class OnboardingData(BaseModel):
    """
    Schema for user onboarding data.
    """
    first_name: str = Field(..., min_length=1, max_length=50, description="User's first name")
    last_name: str = Field(..., min_length=1, max_length=50, description="User's last name")
    
    @validator('first_name')
    def validate_first_name(cls, v):
        if not v or not v.strip():
            raise ValueError("First name cannot be empty")
        return v.strip().title()
    
    @validator('last_name')
    def validate_last_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Last name cannot be empty")
        return v.strip().title()


class OnboardingResponse(BaseModel):
    """
    Schema for onboarding completion response.
    """
    message: str
    onboarding_completed: bool
    user_id: UUID
    first_name: str
    last_name: str


class OnboardingStatus(BaseModel):
    """
    Schema for checking onboarding status.
    """
    user_id: UUID
    email: str
    is_verified: bool
    onboarding_completed: bool
    requires_onboarding: bool
