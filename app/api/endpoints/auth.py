from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import EmailStr

from app.api.deps import get_db
from app.core.config import settings
from app.schemas.token import Token
from app.schemas.user import User, UserCreate
from app.services import user as user_service
from app.utils.security import create_access_token

router = APIRouter()

@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    Login and return an access token.
    
    Args:
        db: SQLAlchemy session
        form_data: OAuth2 password request form containing email and password
    Returns:
        Token object containing access token and token type
    Raises:
        HTTPException: If credentials are invalid
    """
    user = user_service.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user_service.is_active(user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate = Body(...),
) -> Any:
    """
    Register a new user.
    
    Args:
        db: SQLAlchemy session
        user_in: UserCreate object containing user details
    Returns:
        Created User object
    Raises:
        HTTPException: If email already exists
    """
    user = user_service.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="user with this email already exists",
        )
    user = user_service.create(db=db, obj_in=user_in)
    return user

@router.post("/password-recovery/{email}",  response_model=dict, status_code=status.HTTP_200_OK)
def recover_password(email: EmailStr, db: Session = Depends(get_db)) -> Any:
    """
    Initiate password recovery process.
    
    Args:
        email: User's email address
        db: SQLAlchemy session
    Returns:
        Success message
    Raises:
        HTTPException: If user not found
    """
    user = user_service.get_by_email(db, email=email)
    if not user:
        # Dont reveal that the user does not exist - enumeration prevention
        return {"message": "Password recovery email sent"}
    # Here the system would typically send a password recovery email
    return {"message": "Password recovery email sent."}

