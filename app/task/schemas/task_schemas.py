from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

from app.task.models.task_models import TaskStatus, TaskPriority, AssignmentType


class TaskBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    priority: TaskPriority = Field(TaskPriority.MEDIUM, description="Task priority level")
    due_date: Optional[datetime] = None


class TaskCreate(TaskBase):
    project_id: UUID
    assignment_type: AssignmentType = Field(AssignmentType.ADMIN_ASSIGNED, description="How the task is assigned")
    assignee_id: Optional[UUID] = Field(None, description="User assigned to task (null for general pool)")


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    assignee_id: Optional[UUID] = None


class TaskOut(TaskBase):
    id: UUID
    project_id: UUID
    assignee_id: Optional[UUID]
    created_by_id: UUID
    status: TaskStatus
    assignment_type: AssignmentType
    created_at: datetime
    updated_at: datetime
    
    # Optional user info (populated by service)
    assignee_email: Optional[str] = None
    created_by_email: Optional[str] = None

    class Config:
        from_attributes = True


class TaskClaim(BaseModel):
    """Schema for claiming a task from general pool"""
    pass 


class GeneralPoolTaskOut(TaskOut):
    """Schema for general pool tasks - might hide some sensitive info"""
    pass  
