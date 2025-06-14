from sqlalchemy import ForeignKey, String, Text, Enum, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import uuid4
from datetime import datetime, timezone
from enum import Enum as PyEnum

from app.db.base import Base
from app.project.models.project_models import Project
from app.user.models.user_models import User
import uuid


class TaskStatus(PyEnum):
    NOT_STARTED = "NOT_STARTED"    
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"           
    COMPLETED = "COMPLETED"


class TaskPriority(PyEnum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class AssignmentType(PyEnum):
    ADMIN_ASSIGNED = "ADMIN_ASSIGNED" # Directly assigned by an admin
    GENERAL_POOL = "GENERAL_POOL"    # Available for any one to claim


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    priority: Mapped[TaskPriority] = mapped_column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    assignment_type: Mapped[AssignmentType] = mapped_column(Enum(AssignmentType), default=AssignmentType.ADMIN_ASSIGNED)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.NOT_STARTED)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc), nullable=False)

    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id"))
    assignee_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_by_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)

    project: Mapped["Project"] = relationship("Project", back_populates="tasks")
    assignee: Mapped["User"] = relationship("User", foreign_keys= [assignee_id], back_populates="tasks_assigned")
    created_by: Mapped["User"] = relationship("User", foreign_keys=[created_by_id])
