from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

from app.task.models.task_models import TaskStatus


class TaskBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    status: Optional[TaskStatus] = TaskStatus.TODO
    due_date: Optional[datetime] = None


class TaskCreate(TaskBase):
    project_id: UUID
    assignee_id: Optional[UUID] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    due_date: Optional[datetime] = None
    assignee_id: Optional[UUID] = None


class TaskOut(TaskBase):
    id: UUID
    project_id: UUID
    assignee_id: Optional[UUID]

    class Config:
        from_attributes = True
