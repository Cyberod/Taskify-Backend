from typing import Optional, List, Any, Dict, Union
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.security import get_password_hash, verify_password


def get_by_email(db: Session, email: str) -> Optional[User]:
    """
    Retrieve a user by their email address.
    
    Args:
        db: SQLAlchemy session
        email: Email address of the user to retrieve
        
    Returns:
        User object if found, None otherwise
    """
    return db.query(User).filter(User.email == email).first()
def get_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Retrieve a user by their ID.

    Args:
        db: SQLAlchemy session
        user_id: ID of the user to retrieve

    Returns:
        User object if found, None otherwise
    """
    return db.query(User).filter(User.id == user_id).first()

def get_multi(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """
    Retrieve multiple users with pagination.

    Args:
        db: SQLAlchemy session
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return

    Returns:
        List of User objects
    """
    return db.query(User).offset(skip).limit(limit).all()

def create(db: Session, user: UserCreate) -> User:
    """
    Create a new user.

    Args:
        db: SQLAlchemy session
        user: UserCreate object containing user details

    Returns:
        Created User object

    Raises:
        IntegrityError: If the email is already registered
    """
    try:
        db_obj = User(
            email=user.email,
            hashed_password=get_password_hash(user.password),
            is_active=True
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",

        )
    
def update(db:Session,
    *,
    db_obj: User,
    obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
    """
    Update an existing user.

    Args:
    db: Database(Sqlalchemy) session
    db_obj: User object to be updated
    obj_in: UserUpdate object or dictionary containing updated user details

    Returns:
    Updated User object
    """
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.dict(exclude_unset=True)

    # Handle password update securely
    if "password" in update_data:
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password

    # update fields
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    try:
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )


def delete(db: Session, *, user_id: int) -> User:
    """
    Delete a user by their ID.

    Args:
        db: SQLAlchemy session
        user_id: ID of the user to delete

    Returns:
        Deleted User object
    """
    user = get_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    db.delete(user)
    db.commit()
    return user

def authenticate(db: Session, *, email: str, password: str) -> Optional[User]:
    """
    Authenticate a user by their email and password.

    Args:
        db: SQLAlchemy session
        email: Email address of the user
        password: Password of the user
    Returns:
        Authenticated User object if credentials are valid, None otherwise
    """
    user = get_by_email(db, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def is_active(user: User) -> bool:
    """
    Check if a user is active.

    Args:
        user: User object

    Returns:
        True if the user is active, False otherwise
    """
    return user.is_active




        