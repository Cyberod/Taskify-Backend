from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
import datetime
from datetime import timezone

from app.db.session import Base

def utc_now():
    """Returns the current UTC datetime."""
    return datetime.now(timezone.utc)

# Association table for project members
project_members = Table(
    "project_members",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("project_id", Integer, ForeignKey("projects.id"), primary_key=True),
    Column("is_admin", Boolean, default=False),
    Column("joined_at", DateTime(timezone=True), default=utc_now),
)


class User(Base):
    """
    User model for authentication and user management.
    
    Attributes:
        id: Primary key
        email: User's email address (unique)
        hashed_password: Securely hashed password
        avatar_url: URL to the user's avatar image
        is_active: Whether the user account is active
        created_at: When the user was created
        updated_at: When the user was last updated
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    avatar_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)


    # Relationships
    owned_projects = relationship("Project", back_populates="owner")
    projects = relationship("Project", secondary=project_members, back_populates="members")
    assigned_tasks = relationship("Task", back_populates="assignee")
    created_tasks = relationship("Task", back_populates="creator")
    comments = relationship("Comment", back_populates="author")
    notifications = relationship("Notification", back_populates="user")