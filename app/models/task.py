from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Text, Enum
from sqlalchemy.orm import relationship
import datetime, enum
from datetime import timezone

from app.db.session import Base

def utc_now():
    """Returns the current UTC datetime."""
    return datetime.now(timezone.utc)


class TaskStatus(str, enum.Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"

""" class TaskPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL" """ # Uncomment this if you want to use TaskPriority enum


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.NOT_STARTED)
    # priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    is_general_pool = Column(Boolean, default=False)
    deadline = Column(DateTime, nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    # Relationships
    project = relationship("Project", back_populates="tasks")
    creator = relationship("User", back_populates="created_tasks")
    assignee = relationship("User", back_populates="assigned_tasks")
    comments = relationship("Comment", back_populates="task")
    notifications = relationship("Notification", back_populates="task")
    attachments = relationship("Attachment", back_populates="task", cascade="all, delete-orphan")