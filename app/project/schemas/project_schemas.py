from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from app.project.models.project_models import ProjectStatus



class ProjectBase(BaseModel):
    name: str = Field(..., max_length=255, description="Name of the project")
    description: str | None = Field(None, max_length=1000, description="Description of the project")
    status: ProjectStatus = Field(ProjectStatus.ACTIVE, description="Current status of the project")
    color: str | None = Field("#3b82f6", max_length=7, description="Project color in hex format")
    icon: str | None = Field("folder", max_length=50, description="Project icon name")
    deadline: datetime | None = Field(None, description="Project deadline")


class ProjectCreate(ProjectBase):
    pass



class ProjectUpdate(BaseModel):
    name: str | None = Field(None, max_length=255, description="Name of the project")
    description: str | None = Field(None, max_length=1000, description="Description of the project")
    status: ProjectStatus | None = Field(None, description="Current status of the project")
    color: str | None = Field(None, max_length=7, description="Project color in hex format")
    icon: str | None = Field(None, max_length=50, description="Project icon name")
    deadline: datetime | None = Field(None, description="Project deadline")


class ProjectRead(ProjectBase):
    id: UUID = Field(..., description="Unique identifier of the project")
    created_at: datetime = Field(..., description="Timestamp when the project was created")
    owner_id: UUID = Field(..., description="ID of the user who owns the project")


    class Config:
        from_attributes = True


class ProjectOut(ProjectRead):
    id: UUID = Field(..., description="Unique identifier of the project")
    owner_id: UUID = Field(..., description="ID of the user who owns the project")
    created_at: datetime = Field(..., description="Timestamp when the project was created")
    updated_at: datetime = Field(..., description="Timestamp when the project was last updated")

    class Config:
        from_attributes = True
