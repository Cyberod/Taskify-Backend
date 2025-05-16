from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.user.schemas.user import UserCreate, UserResponse
from app.user.services.user import create_user

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Endpoint to create a new user.

    Args:
        user_data (UserCreate): The data for the new user.
        db (AsyncSession): The database session.

    Returns:
        UserResponse: The created user object.
    """
    return await create_user(user_data, db)