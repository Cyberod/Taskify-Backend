from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.config import settings
from app.db.session import get_db
from app.user.models.user_models import User, UserRole, BlacklistedToken
from app.user.schemas.user_schema import TokenData
from app.user.services.user_services import get_user_by_id
from sqlalchemy import select


oauth2_scheme = settings.oauth2_scheme

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get the current user from the token.

    Args:
        token (str): The JWT token.
        db (AsyncSession): The database session.

    Returns:
        User: The user object.

    Raises:
        HTTPException: If the token is invalid or the user is not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        jti: str = payload.get("jti")
        if user_id is None or jti is None:
            raise credentials_exception
        token_data = TokenData(sub=user_id)
        stmt = select(BlacklistedToken).where(BlacklistedToken.jti == jti)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await get_user_by_id(UUID(user_id), db)
    if user is None:
        raise credentials_exception

    return user



async def get_current_user_with_onboarding_check(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get the current user and ensure onboarding is completed.
    This should be used for endpoints that require full user setup.

        Args:
            token (str): The JWT token.
            db (AsyncSession): The database session.

        Returns:
            User: The user object.

        Raises:
            HTTPException: If the token is invalid, user is not found, or onboarding is incomplete.
    """
    user = await get_current_user(token, db)
    
    # Check if user has completed onboarding
    if user.is_verified and not user.onboarding_completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Onboarding must be completed before accessing this resource",
            headers={"X-Onboarding-Required": "true"}
        )
    
    return user


async def require_admin_user(
    current_user: User = Depends(get_current_user_with_onboarding_check),
) -> User:
    """
    Dependency to ensure the current user is an admin.

    Args:
        current_user (User): The current user.

    Returns:
        User: The current user object.

    Raises:
        HTTPException: If the user is not an admin.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action.",
        )
    return current_user