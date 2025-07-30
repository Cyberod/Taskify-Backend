import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.db.session import get_db
from app.user.models.user_models import User
from app.project.models.project_models import Project
from app.project.models.file_models import ProjectFile
from app.project.schemas.file_schemas import ProjectFileOut, ProjectFileCreate, ProjectFileUpdate
from app.core.file_storage import file_storage
from app.project.dependencies.project_dependencies import require_project_member

router = APIRouter(prefix="/projects", tags=["files"])


@router.post("/{project_id}/files", response_model=ProjectFileOut)
async def upload_file(
    project_id: uuid.UUID,
    file: UploadFile = File(...),
    description: str = Form(None),
    current_user: User = Depends(require_project_member),
    db: AsyncSession = Depends(get_db)
):
    """Upload a file to a project"""
    
    # Validate file type
    if not file_storage.validate_file_type(file.filename):
        raise HTTPException(status_code=400, detail="File type not allowed")
    
    # Save file to storage
    stored_filename, file_path = await file_storage.save_file(file, str(project_id))
    
    # Create database record
    project_file = ProjectFile(
        filename=stored_filename,
        original_filename=file.filename,
        file_path=file_path,
        file_size=len(await file.read()),
        mime_type=file.content_type or "application/octet-stream",
        description=description,
        project_id=project_id,
        uploaded_by=current_user.id
    )
    
    # Reset file position after reading for size
    await file.seek(0)
    
    db.add(project_file)
    await db.commit()
    await db.refresh(project_file)
    
    # Return file info with download URL
    result = ProjectFileOut.model_validate(project_file)
    result.download_url = f"/projects/{project_id}/files/{project_file.id}/download"
    
    return result


@router.get("/{project_id}/files", response_model=List[ProjectFileOut])
async def list_project_files(
    project_id: uuid.UUID,
    current_user: User = Depends(require_project_member),
    db: AsyncSession = Depends(get_db)
):
    """Get all files in a project"""
    
    # Get all files for this project
    stmt = select(ProjectFile).where(ProjectFile.project_id == project_id)
    result = await db.execute(stmt)
    files = result.scalars().all()
    
    # Add download URLs
    files_with_urls = []
    for file in files:
        file_out = ProjectFileOut.model_validate(file)
        file_out.download_url = f"/projects/{project_id}/files/{file.id}/download"
        files_with_urls.append(file_out)
    
    return files_with_urls


@router.get("/{project_id}/files/{file_id}/download")
async def download_file(
    project_id: uuid.UUID,
    file_id: uuid.UUID,
    current_user: User = Depends(require_project_member),
    db: AsyncSession = Depends(get_db)
):
    """Download a file from a project"""
    
    # Get file record
    stmt = select(ProjectFile).where(
        and_(
            ProjectFile.id == file_id,
            ProjectFile.project_id == project_id
        )
    )
    result = await db.execute(stmt)
    project_file = result.scalar_one_or_none()
    
    if not project_file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Get file path and check if exists
    file_path = file_storage.get_file_path(project_file.file_path)
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    return FileResponse(
        path=str(file_path),
        filename=project_file.original_filename,
        media_type=project_file.mime_type
    )


@router.put("/{project_id}/files/{file_id}", response_model=ProjectFileOut)
async def update_file(
    project_id: uuid.UUID,
    file_id: uuid.UUID,
    file_update: ProjectFileUpdate,
    current_user: User = Depends(require_project_member),
    db: AsyncSession = Depends(get_db)
):
    """Update file metadata (description only)"""
    
    # Get file record
    stmt = select(ProjectFile).where(
        and_(
            ProjectFile.id == file_id,
            ProjectFile.project_id == project_id
        )
    )
    result = await db.execute(stmt)
    project_file = result.scalar_one_or_none()
    
    if not project_file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Update description
    if file_update.description is not None:
        project_file.description = file_update.description
    
    await db.commit()
    await db.refresh(project_file)
    
    # Return updated file info
    result = ProjectFileOut.model_validate(project_file)
    result.download_url = f"/projects/{project_id}/files/{project_file.id}/download"
    
    return result


@router.delete("/{project_id}/files/{file_id}")
async def delete_file(
    project_id: uuid.UUID,
    file_id: uuid.UUID,
    current_user: User = Depends(require_project_member),
    db: AsyncSession = Depends(get_db)
):
    """Delete a file from a project"""
    
    # Get file record
    stmt = select(ProjectFile).where(
        and_(
            ProjectFile.id == file_id,
            ProjectFile.project_id == project_id
        )
    )
    result = await db.execute(stmt)
    project_file = result.scalar_one_or_none()
    
    if not project_file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Delete file from storage
    await file_storage.delete_file(project_file.file_path)
    
    # Delete from database
    await db.delete(project_file)
    await db.commit()
    
    return {"message": "File deleted successfully"}
