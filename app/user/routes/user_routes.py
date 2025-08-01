from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError
from jose import JWTError, jwt



from app.db.session import get_db
from app.user.schemas.user_schema import UserCreate, UserResponse
from app.user.services.user_services import create_user
from app.user.dependencies.user_dependencies import get_current_user, get_current_user_with_onboarding_check
from app.user.models.user_models import User, UserRole, BlacklistedToken 
from app.user.services.user_verification_service import send_verification_code
from app.core.config import settings




router = APIRouter(prefix="/users", tags=["users"])

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Endpoint to create a new user.
    User account will be created but inactive until email verification.

        Args:
            user_data (UserCreate): The data for the new user.
            db (AsyncSession): The database session.

        Returns:
            UserResponse: The created user object.

        Raises:
            HTTPException: If the email already exists in the database.
            HTTPException: If the email or password is not provided.
    """
    try:
        # Create user (will be inactive by default)
        user = await create_user(user_data, db)
        
        # Send verification email
        try:
            await send_verification_code(user.email, db)
        except Exception as e:
            # Log the error but don't fail the signup
            print(f"Failed to send verification email: {e}")
        
        return user
        
    except ValidationError as e:
        error_messages = []
        for error in e.errors():
            error_messages.append(error["msg"])
        raise HTTPException(
            status_code=400,
            detail=f"Invalid input: {', '.join(error_messages)}"
        )
    except HTTPException:
        # Re-raise HTTP exceptions from create_user (like email already exists)
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during signup"
        )

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
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "avatar_url": current_user.avatar_url,
        "role": current_user.role,
        "is_verified": current_user.is_verified,
        "onboarding_completed": current_user.onboarding_completed,
        "requires_onboarding": current_user.is_verified and not current_user.onboarding_completed,
    }


@router.get("/profile")
async def get_user_profile(current_user: User = Depends(get_current_user_with_onboarding_check)):
    """
    Get full user profile. This endpoint requires completed onboarding.

        Args:
            current_user (User): The current user with completed onboarding.

        Returns:
            dict: The current user profile.
    """
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "full_name": f"{current_user.first_name} {current_user.last_name}",
        "avatar_url": current_user.avatar_url,
        "role": current_user.role,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at
    }

@router.get("/admin")
async def admin_only_route(current_user: User = Depends(get_current_user_with_onboarding_check)):
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
        "full_name": f"{current_user.first_name} {current_user.last_name}",
    }

@router.post("/logout")
async def logut(current_user: User = Depends(get_current_user), token: str = Depends(settings.oauth2_scheme), db: AsyncSession = Depends(get_db)):
    """
    Endpoint to log out the current user by blacklisting the token.

        Args:
            current_user (User): The current user.
            token (str): The JWT token.
            db (AsyncSession): The database session.

        Returns:
            dict: A message indicating the user has been logged out.

        Raises:
            HTTPException: If the token is invalid or the user is not found.
    """

    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        jti = payload.get("jti")
        if jti is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        blacklisted_token = BlacklistedToken(jti=jti)
        db.add(blacklisted_token)
        await db.commit()
        return {
            "message": "Logged out successfully",
            "user_id": str(current_user.id),
            "email": current_user.email,

        }   
    except (JWTError, IntegrityError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Logout failed",
        )


    


