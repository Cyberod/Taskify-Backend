from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.task.models.task_models import Task
from app.task.schemas.task_schemas import TaskCreate, TaskUpdate
from app.project.services import project_services
from app.project.utils.project_utils import recalculate_project_completion

from fastapi import Depends, HTTPException


async def create_task(project_id: UUID, task_data: TaskCreate, db: AsyncSession, current_user_id: UUID,) -> Task:
    """Create a new task in the database.
        Args:

        project_id (UUID): The ID of the project to which the task belongs.
        task_data (TaskCreate): The data for the task to be created.
        db (AsyncSession): The database session.

        Returns:
        Task: The created task object.
        
    """
    project = await project_services.get_project_by_id(task_data.project_id, db)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project with ID {task_data.project_id} not found.")

    if project.owner_id != current_user_id:
        raise HTTPException(status_code=404, detail=f"Access Denied. You are not the owner of the project {task_data.project_id}.")
    
    task = Task(**task_data.model_dump(), project_id=project_id)
    db.add(task)
    await db.commit()
    await db.refresh(task)
    await recalculate_project_completion(project_id, db)
    return task


async def get_task_by_id(task_id: UUID, db: AsyncSession) -> Task | None:
    """Retrieve a task by its ID.

        Args:

        task_id (UUID): The ID of the task to retrieve.
        db (AsyncSession): The database session.

        Returns: 
        Task | None: The task object if found, otherwise None.
    """
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found.")
    return task


async def get_tasks_by_project(project_id: UUID, db: AsyncSession) -> list[Task]:
    """Retrieve all tasks associated with a specific project.

        Args:

        project_id (UUID): The ID of the project to retrieve tasks for.
        db (AsyncSession): The database session.

        Returns:
        list[Task]: A list of task objects associated with the project.
    """
    result = await db.execute(select(Task).where(Task.project_id == project_id))
    return result.scalars().all()


async def update_task(task_id: UUID, task_data: TaskUpdate, db: AsyncSession) -> Task | None:
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if task is None:
        return None

    for field, value in task_data.model_dump(exclude_unset=True).items():
        setattr(task, field, value)

    await db.commit()
    await db.refresh(task)
    await recalculate_project_completion(task.project_id, db)
    return task


async def delete_task(task_id: UUID, db: AsyncSession) -> bool:
    task = await get_task_by_id(task_id, db)
    project_id = task.project_id

    await db.delete(task)
    await db.commit()
    await recalculate_project_completion(project_id, db)
    return {"messge": "Task deleted successfully."}


async def get_tasks_by_user(user_id: UUID, db: AsyncSession) -> list[Task]:
    """Retrieve all tasks assigned to a specific user.

            Args:

            user_id (UUID): The ID of the user to retrieve tasks for.
            db (AsyncSession): The database session.

            Returns:
            list[Task]: A list of task objects assigned to the user.
    """
    result = await db.execute(select(Task).where(Task.assigned_to == user_id))
    return result.scalars().all()
