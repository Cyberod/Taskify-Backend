from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr
from enum import Enum



class InviteStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


# Base Schema

class ProjectInviteBase(BaseModel):
    email: EmailStr


# Schema for creating a new invite
class ProjectInviteCreate(ProjectInviteBase):
    pass


# schema returned to client (readable format)
class ProjectInviteRead(ProjectInviteBase):
    id: UUID
    project_id: UUID
    token: str
    status: InviteStatus
    created_at: datetime
    expires_at: datetime | None

    class Config:
        form_attributes = True


# Schema for accepting an invite
class AcceptInvite(BaseModel):
    token: str


# schema for declining an invite (optional for now, I will discuss with the Team)
class DeclineInvite(BaseModel):
    token: str