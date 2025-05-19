from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.user.schemas.user_schema import UserCreate, UserResponse
from app.user.services.user_services import create_user
from app.user.dependencies.user_dependencies import get_current_user
from app.user.models.user_models import User, UserRole

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

        Raises:
            HTTPException: If the email already exists in the database.
            HttpException: If the email or password is not provided.
    """
    if not user_data.email or not user_data.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required",
        )
    
    return await create_user(user_data, db)

@router.get("/me")
async def get_current_user_data(current_user: User = Depends(get_current_user)):
    """
    Dependency to get the current user.

        Args:
            current_user (User): The current user.

        Returns:
            User: The current user object.

        Raises:
            HTTPException: If the user is not authenticated.


    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "avatar_url": current_user.avatar_url,
        "role": current_user.role,
    }


@router.get("/admin")
async def admin_only_route(current_user: User = Depends(get_current_user)):
    """
    Admin-only route to demonstrate role-based access control.

        Args:
            current_user (User): The current user.

        Returns:
        dict: A message indicating the user is an admin.
        
        Raises:
        HTTPException: If the user is not an admin.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have the required permissions",
        )
    return {
        "message": "Welcome, Admin!",
        "user_id": str(current_user.id),
        "email": current_user.email,
    }
