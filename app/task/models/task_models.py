from sqlalchemy import ForeignKey, String, Text, Enum, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import uuid4
from datetime import datetime
from enum import Enum as PyEnum

from app.db.base import Base
from app.project.models.project_models import Project
from app.user.models.user_models import User
import uuid


class TaskStatus(PyEnum):
    TODO = "TO DO"
    IN_PROGRESS = "IN PROGRESS"
    COMPLETED = "COMPLETED"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.TODO)
    due_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id"))
    assignee_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=True)

    project: Mapped["Project"] = relationship(back_populates="tasks")
    assignee: Mapped["User"] = relationship(back_populates="tasks_assigned")
