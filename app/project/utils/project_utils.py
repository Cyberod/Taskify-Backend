from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.task.models.task_models import Task, TaskStatus
from app.project.models.project_models import Project
from uuid import UUID


async def recalculate_project_completion(project_id: UUID, db: AsyncSession):
    """
    Recalculate the completion of a project based on completed tasks

        Args:
            project_id (UUID): The ID of the project.
            db (AsyncSession): The database session.
    """
    total_tasks_query = select(func.count(Task.id)).where(Task.project_id == project_id)
    completed_tasks_query = select(func.count(Task.id)).where(
        Task.project_id == project_id, 
        Task.status == TaskStatus.COMPLETED
    )

    total_tasks = (await db.execute(total_tasks_query)).scalar()
    completed_tasks = (await db.execute(completed_tasks_query)).scalar()

    completion = (completed_tasks / total_tasks * 100) if total_tasks else 0

    project_query = select(Project).where(Project.id == project_id)
    result = await db.execute(project_query)
    project = result.scalar_one_or_none()

    if project:
        project.completion_percentage = completion
        db.add(project)
        await db.commit()
        await db.refresh(project)

