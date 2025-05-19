from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.user.schemas.user import UserCreate, UserResponse
from app.user.services.user import create_user
from app.auth.utils.jwt_handler import get_current_user
from app.user.models.user import User

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

@router.get("/me")
async def get_current_user_data(current_user: User = Depends(get_current_user)):
    """
    Dependency to get the current user.

    Args:
        current_user (User): The current user.

    Returns:
        User: The current user object.
    """
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "avatar_url": current_user.avatar_url,
        "role": current_user.role,
    }