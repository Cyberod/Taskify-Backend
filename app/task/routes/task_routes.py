from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional, List

from app.db.session import get_db
from app.user.dependencies.user_dependencies import get_current_user
from app.user.models.user_models import User
from app.task.services import task_services
from app.task.models.task_models import TaskPriority, AssignmentType, TaskStatus
from app.task.schemas.task_schemas import TaskCreate, TaskUpdate, TaskOut, GeneralPoolTaskOut


router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new task"""
    return await task_services.create_task(task_data, db, current_user.id)



@router.get("/{task_id}", response_model=TaskOut)
async def get_task_by_id(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get specific task by ID"""
    return await task_services.get_task_by_id(task_id, db, current_user.id)


@router.get("/project/{project_id}", response_model=list[TaskOut])
async def get_tasks_by_project(
    project_id: UUID,
    assignment_type: Optional[AssignmentType] = Query(None, description="Filter by assignment type"),
    status: Optional[TaskStatus] = Query(None, description="Filter by status"),
    priority: Optional[TaskPriority] = Query(None, description="Filter by task priority"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all tasks for project with optional filtering"""
    tasks = await task_services.get_tasks_by_project(project_id, db, current_user.id, assignment_type, status, priority)
    return tasks


# Claim Task Endpoint
@router.post("/{task_id}/claim", response_model=TaskOut)
async def claim_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Claim a task from the general pool"""
    return await task_services.claim_task(task_id, db, current_user.id)

@router.put("/{task_id}", response_model=TaskOut)
async def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing Task"""
    return task_services.update_task(task_id, task_data, db, current_user.id)

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a Specific task"""

    await task_services.delete_task(task_id, db, current_user.id)



# Get User's Assigned Tasks
@router.get("/user/assigned", response_model=List[TaskOut])
async def get_my_assigned_tasks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all tasks assigned to the current user"""
    return await task_services.get_user_assigned_tasks(current_user.id, db)

# General Pool Tasks
@router.get("/project/{project_id}/pool", response_model=List[GeneralPoolTaskOut])
async def get_general_pool_tasks(
    project_id: UUID,
    priority: Optional[TaskPriority] = Query(None, description="Filter by priority"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get available tasks from the general pool that can be claimed"""
    return await task_services.get_general_pool_tasks(project_id, db, current_user.id, priority)