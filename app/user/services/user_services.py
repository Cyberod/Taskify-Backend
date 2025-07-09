from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.auth.utils.hashing import Hasher
from app.user.models.user_models import User
from app.user.schemas.user_schema import UserCreate
from uuid import UUID


async def create_user(user_data: UserCreate, db: AsyncSession) -> User:
    """
    Create a new user in the database.

    Args:
        user_data (UserCreate): The data for the new user.
        db (AsyncSession): The database session.

    Returns:
        User: The created user object.

    Raises:
        HTTPException: If the email already exists in the database.
    """
    user = User(
        email=user_data.email,
        password=Hasher.get_password_hash(user_data.password),
        avatar_url=user_data.avatar_url,
        is_active=False,  # User will be inactive until verified
        is_verified=False,  # User will be unverified initially
    )

    db.add(user)
    try:
        await db.commit()
        await db.refresh(user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    return user


async def get_user_by_id(user_id: UUID, db: AsyncSession) -> User:
    """
    Get a user by their ID.

    Args:
        user_id (UUID): The ID of the user.
        db (AsyncSession): The database session.

    Returns:
        User: The user object.

    Raises:
        HTTPException: If the user is not found.
    """
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user

