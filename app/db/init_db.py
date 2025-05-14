import logging
from sqlalchemy.orm import Session

from app.schemas.user import UserCreate
from app.services import user as user_service
from app.core.config import settings

logger = logging.getLogger(__name__)

def init_db(db: Session) -> None:
    """
    Initialize database with initial data.
    
    This function creates an initial admin user if one doesn't exist.
    
    Args:
        db: Database session
    """
    # Check if we should create initial admin user
    user = user_service.get_by_email(db, email="admin@taskify.com")
    if not user:
        logger.info("Creating initial admin user")
        user_in = UserCreate(
            email="admin@taskify.com",
            password="adminpassword",  # This should be changed after first login
            full_name="Initial Admin",
        )
        user = user_service.create(db, obj_in=user_in)
        logger.info(f"Initial admin user created with email: {user.email}")
    else:
        logger.info("Admin user already exists, skipping creation")
