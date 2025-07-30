from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class ProjectFileBase(BaseModel):
    filename: str = Field(..., max_length=255, description="Stored filename")
    original_filename: str = Field(..., max_length=255, description="Original filename when uploaded")
    file_size: int = Field(..., description="File size in bytes")
    mime_type: str = Field(..., max_length=100, description="MIME type of the file")
    description: str | None = Field(None, max_length=1000, description="Optional file description")


class ProjectFileCreate(BaseModel):
    description: str | None = Field(None, max_length=1000, description="Optional file description")


class ProjectFileUpdate(BaseModel):
    description: str | None = Field(None, max_length=1000, description="Optional file description")


class ProjectFileRead(ProjectFileBase):
    id: UUID = Field(..., description="Unique identifier of the file")
    project_id: UUID = Field(..., description="ID of the project this file belongs to")
    uploaded_by: UUID = Field(..., description="ID of the user who uploaded the file")
    created_at: datetime = Field(..., description="Timestamp when the file was uploaded")
    updated_at: datetime = Field(..., description="Timestamp when the file was last updated")

    class Config:
        from_attributes = True


class ProjectFileOut(ProjectFileRead):
    download_url: str | None = Field(None, description="URL to download the file")

    class Config:
        from_attributes = True
