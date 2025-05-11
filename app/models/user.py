from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
import datetime

from app.db.session import Base
from app.models.task import Task
from app.db.session import Base

# Association table for project members
project_members = Table(
    "project_members",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("project_id", Integer, ForeignKey("projects.id"), primary_key=True),
    Column("is_admin", Boolean, default=False),
    Column("joined_at", DateTime, default=datetime.datetime.utcnow),
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


    # Relationships
    owned_projects = relationship("Project", back_populates="owner")
    projects = relationship("Project", secondary=project_members, back_populates="members")
    assigned_tasks = relationship("Task", back_populates="assignee")
    created_tasks = relationship("Task", back_populates="creator")
    comments = relationship("Comment", back_populates="author")
    notifications = relationship("Notification", back_populates="user")