from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.user import User as UserSchema, UserUpdate
from app.services import user as user_service

router = APIRouter()

@router.get("/me", response_model=UserSchema)
def read_user_me(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get current user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user information
    """
    return current_user

@router.put("/me", response_model=UserSchema)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate = Body(...),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update own user information.
    
    Args:
        db: Database session
        user_in: User update data
        current_user: Current authenticated user
        
    Returns:
        Updated user information
    """
    # Check if email is being updated and already exists
    if user_in.email and user_in.email != current_user.email:
        user = user_service.get_by_email(db, email=user_in.email)
        if user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )
    
    user = user_service.update(db, db_obj=current_user, obj_in=user_in)
    return user

@router.get("/me/items", response_model=dict)
def read_own_items(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve items owned by current user.
    
    This is a placeholder endpoint that will be implemented
    when we have the project and task models.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User's items
    """
    return {
        "user_id": current_user.id,
        "message": "This endpoint will return the user's projects and tasks"
    }
