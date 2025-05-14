from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.token import TokenPayload
from app.core.config import settings
from app.services import user as user_service

# OAuth2 password bearer flow for token authentication
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

def get_current_user(
    db: Session = Depends(get_db), 
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Validate access token and return current user.
    
    Args:
        db: Database session
        token: JWT token from request
        
    Returns:
        Current authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        
        # Check token expiration
        if token_data.exp is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has no expiration",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = user_service.get_by_id(db, user_id=token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current user and verify they are active.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current active user
        
    Raises:
        HTTPException: If user is inactive
    """
    if not user_service.is_active(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user

def get_project_admin(
    project_id: int, 
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
) -> User:
    """
    Verify current user is an admin of the specified project.
    
    This is a placeholder that will be implemented when we have project models.
    For now, it just returns the current user.
    
    Args:
        project_id: ID of the project
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Current user if they are a project admin
        
    Raises:
        HTTPException: If user is not a project admin
    """
    # This will be implemented later when we have project models
    # For now, we'll just return the current user
    return current_user
