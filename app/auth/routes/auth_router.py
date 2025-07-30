from fastapi import APIRouter, Depends, HTTPException, Request, status, Form
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from app.user.schemas.user_schema import UserLogin
from app.auth.services.auth_service import authenticate_user
from app.db.session import get_db
from fastapi.security import OAuth2PasswordRequestForm
from app.auth.utils.email_sender import get_user_by_email
from typing import Optional

router = APIRouter(tags=["Auth"])

@router.post("/login")
async def login(
    request: Request,
    db: AsyncSession = Depends(get_db),
    # OAuth2 form data parameters (for Swagger UI)
    username: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    # JSON body parameter (for frontend)
    user_data: Optional[UserLogin] = None
):
    """
    Unified login endpoint that accepts both OAuth2 form data and JSON.
    
    For Swagger UI: Use form fields (username=email, password)
    For Frontend: Use JSON body with 'email' and 'password'
    """
    try:
        # Determine request type based on Content-Type header
        content_type = request.headers.get("content-type", "")
        
        if "application/json" in content_type:
            # Handle JSON request (frontend)
            if not user_data:
                raise HTTPException(
                    status_code=400,
                    detail="JSON body with email and password is required"
                )
            login_data = user_data
        else:
            # Handle form data request (Swagger UI / OAuth2)
            if not username or not password:
                raise HTTPException(
                    status_code=400,
                    detail="Username (email) and password are required"
                )
            # Convert OAuth2 form to UserLogin schema (username = email)
            login_data = UserLogin(email=username, password=password)
        
        # Common authentication logic
        user = await get_user_by_email(login_data.email, db)
        if user and not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account not verified. Please check your email for the verification code."
            )
        
        token = await authenticate_user(login_data, db)
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