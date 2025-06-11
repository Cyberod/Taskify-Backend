from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from enum import Enum
from app.project.models.project_models import ProjectRole


class ProjectRoleEnum(str, Enum):
    """Schema enum for project roles"""
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"
    GUEST = "GUEST"


class ProjectMemberBase(BaseModel):
    """Base schema for project members"""
    role: ProjectRoleEnum


class ProjectMemberCreate(ProjectMemberBase):
    """Schema for creating a project member"""
    user_id: UUID
    project_id: UUID


class ProjectMemberUpdate(BaseModel):
    """Schema for updating a project member's role"""
    role: ProjectRoleEnum


class ProjectMemberRead(ProjectMemberBase):
    """Schema for reading project member data"""
    id: UUID
    project_id: UUID
    user_id: UUID
    joined_at: datetime
    
    # User info (we'll populate this in the service)
    user_email: str | None = None
    user_avatar_url: str | None = None

    class Config:
        from_attributes = True


class ProjectMemberWithUser(ProjectMemberRead):
    """Extended schema with full user details"""
    user_email: str
    user_avatar_url: str | None = None

    class Config:
        from_attributes = True
