from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from app.user.schemas.user_schema import UserLogin
from app.auth.services.auth_service import authenticate_user
from app.db.session import get_db
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(tags=["Auth"])

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    Authenticate user and return access token.

        Args:
            form_data (OAuth2PasswordRequestForm): The form data containing username and password.
            db (AsyncSession): The database session.

        Returns:
            dict: A dictionary containing the access token and token type.
        
        Raises:
            HTTPException: If the credentials are invalid.

    """
    # Validate form data
    if not form_data.username or not form_data.username.strip():
        raise HTTPException(
            status_code=400,
            detail="Email/Username is required"
        )
    
    if not form_data.password or not form_data.password.strip():
        raise HTTPException(
            status_code=400,
            detail="Password is required"
        )
    
    try:
        # Validate email format
        user_data = UserLogin(email=form_data.username, password=form_data.password)
        token = await authenticate_user(user_data, db)
        return {"access_token": token, "token_type": "bearer"}

    except ValidationError as e:
        # Handles email validation error
        error_messages = []
        for error in e.errors():
            error_messages.append(error["msg"])
        raise HTTPException(
            status_code=400,
            detail=f"Invalid input: {', '.join(error_messages)}"
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions for invalid credentials
        raise
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred during login: {str(e)}"
        )