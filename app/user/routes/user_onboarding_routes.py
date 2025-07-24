from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.user.dependencies.user_dependencies import get_current_user
from app.user.models.user_models import User
from app.user.schemas.user_onboarding_schema import (
    OnboardingData,
    OnboardingResponse,
    OnboardingStatus
)
from app.user.services.user_onboarding_service import (
    complete_onboarding,
    get_onboarding_status
)


router = APIRouter(prefix="/onboarding", tags=["User Onboarding"])


@router.get("/status", response_model=OnboardingStatus)
async def check_onboarding_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Check the onboarding status for the current user.
    
    Returns:
        OnboardingStatus: The current onboarding status
    """
    return await get_onboarding_status(current_user.id, db)


@router.post("/complete", response_model=OnboardingResponse)
async def complete_user_onboarding(
    onboarding_data: OnboardingData,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Complete the onboarding process by providing first name and last name.
    
    Args:
        onboarding_data (OnboardingData): The onboarding data containing names
        current_user (User): The current authenticated user
        db (AsyncSession): The database session
        
    Returns:
        OnboardingResponse: The completion response
    """
    return await complete_onboarding(current_user.id, onboarding_data, db)
