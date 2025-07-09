from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from app.user.schemas.user_schema import UserLogin
from app.auth.services.auth_service import authenticate_user
from app.db.session import get_db
from fastapi.security import OAuth2PasswordRequestForm
from app.auth.utils.email_sender import get_user_by_email

router = APIRouter(tags=["Auth"])

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    Authenticate user and return access token.
    Only allows login for verified users.

        Args:
            form_data (OAuth2PasswordRequestForm): The form data containing username and password.
            db (AsyncSession): The database session.

        Returns:
            dict: A dictionary containing the access token and token type.
        
        Raises:
            HTTPException: If the credentials are invalid or account is not verified.
    """
    # Validate form data
    if not form_data.username or not form_data.username.strip():
        raise HTTPException(
            status_code=400,
            detail="Email/username is required"
        )
    
    if not form_data.password or not form_data.password.strip():
        raise HTTPException(
            status_code=400,
            detail="Password is required"
        )
    
    try:
        # Check if user exists and get verification status
        user = await get_user_by_email(form_data.username, db)
        
        if user and not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account not verified. Please check your email for the verification code."
            )
        
        # Validate email format and authenticate
        user_data = UserLogin(email=form_data.username, password=form_data.password)
        token = await authenticate_user(user_data, db)
        return {"access_token": token, "token_type": "bearer"}

    except ValidationError as e:
        # Handle email validation errors
        error_messages = []
        for error in e.errors():
            error_messages.append(error["msg"])
        raise HTTPException(
            status_code=400,
            detail=f"Invalid input: {', '.join(error_messages)}"
        )
    except HTTPException:
        # Re-raise HTTP exceptions from authenticate_user
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during login"
        )   