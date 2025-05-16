from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.auth.utils.hashing import Hasher
from app.user.models.user import User
from app.user.schemas.user import UserCreate


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

