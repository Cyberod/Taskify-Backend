from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.db.session import get_db
from app.user.dependencies.user_dependencies import get_current_user
from app.user.models.user_models import User
from app.task.services import task_services
from app.task.models.task_models import Task
from app.task.schemas.task_schemas import TaskCreate, TaskUpdate, TaskOut


router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await task_services.create_task(task_data, db, current_user.id)



@router.get("/{task_id}", response_model=TaskOut)
async def get_task_by_id(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = await task_services.get_task_by_id(task_id, db)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.get("/project/{project_id}", response_model=list[TaskOut])
async def get_tasks_by_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tasks = await task_services.get_tasks_by_project(project_id, db)
    return tasks


@router.put("/{task_id}", response_model=TaskOut)
async def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = await task_services.update_task(task_id, task_data, db)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = await task_services.delete_task(task_id, db)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return {"detail": "Task deleted successfully"}