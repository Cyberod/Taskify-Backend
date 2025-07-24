from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from uuid import UUID

from app.user.models.user_models import User
from app.user.schemas.user_onboarding_schema import OnboardingData, OnboardingResponse, OnboardingStatus

async def complete_onboarding(
    user_id: UUID,
    onboarding_data: OnboardingData,
    db: AsyncSession
) -> OnboardingResponse:
    """
    Complete user onboarding by adding first and last name,

        Args:
            user_id (UUID): The ID of the user completing onboarding.
            onboarding_data (OnboardingData): The data provided by the user during onboarding.
            db (AsyncSession): The database session.
        
        Returns:
            OnboardingResponse: Response containing the onboarding completion status and user details.
    """
    # fetch the user from the database
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # check if user is verified
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_404_BAD_REQUEST,
            detail="Email must be verified before completing onboarding"
        )
    
    # Check if onboarding is already completed
    user.first_name = onboarding_data.first_name
    user.last_name = onboarding_data.last_name
    user.onboarding_completed = True

    try:
        await db.commit()
        await db.refresh(user)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete onboarding"
        )
    
    return OnboardingResponse(
        message="Onboarding completed successfully",
        onboarding_completed=user.onboarding_completed,
        user_id=user.id,
        first_name=user.first_name,
        last_name=user.last_name
    )



async def get_onboarding_status(
    user_id: UUID,
    db: AsyncSession
) -> OnboardingStatus:
    """
    Get the onboarding status of a user.
    
        Args:
            user_id (UUID): The ID of the user.
            db (AsyncSession): The database session.
        
        Returns:
            OnboardingStatus: Status of the user's onboarding.
        
        Raises:
            HTTPException: If the user is not found.
    """
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return OnboardingStatus(
        user_id=user.id,
        email=user.email,
        is_verified=user.is_verified,
        onboarding_completed=user.onboarding_completed,
        requires_onboarding=not user.onboarding_completed
    )