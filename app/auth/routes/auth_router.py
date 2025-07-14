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
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Authenticate user and return access token.
    Accepts JSON body with 'email' and 'password'.
    """
    try:
        # Check if user exists and get verification status
        user = await get_user_by_email(user_data.email, db)
        if user and not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account not verified. Please check your email for the verification code."
            )
        token = await authenticate_user(user_data, db)
        return {"access_token": token, "token_type": "bearer"}
    except ValidationError as e:
        error_messages = [error["msg"] for error in e.errors()]
        raise HTTPException(
            status_code=400,
            detail=f"Invalid input: {', '.join(error_messages)}"
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during login"
        )