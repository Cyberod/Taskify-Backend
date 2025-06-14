from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID

from app.project.schemas.project_schemas import ProjectCreate, ProjectUpdate, ProjectOut
from app.project.services import project_service as services
from app.user.models.user_models import User
from app.user.dependencies.user_dependencies import get_current_user
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/projects", tags=["Projects"])


# Create a new project
@router.post("/", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await services.create_project(data, current_user.id, db)


# Get all projects owned by the current user
@router.get("/", response_model=List[ProjectOut])
async def get_my_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    
    return await services.get_user_projects(current_user.id, db)


# Get a single project by ID
@router.get("/{project_id}", response_model=ProjectOut)
async def get_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    project = await services.get_project_by_id(project_id, db)
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


# Update a project
@router.put("/{project_id}", response_model=ProjectOut)
async def update_project(
    project_id: UUID,
    data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    project = await services.get_project_by_id(project_id, db)
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    return await services.update_project(project_id, data, db)


# Delete a project
@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    project = await services.get_project_by_id(project_id, db)
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    await services.delete_project(project_id, db)
