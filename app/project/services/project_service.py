from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional
from uuid import UUID


from app.project.models.project_models import Project
from app.project.schemas.project_schemas import ProjectCreate, ProjectUpdate


async def create_project(data: ProjectCreate, owner_id: UUID, db: AsyncSession) -> Project:
    """
    Create a new project in the database.

        Args:
            project_data (ProjectCreate): The data for the new project.
            db (AsyncSession): The database session.
            owner_id (UUID): The ID of the user who owns the project.

        Returns:
            Project: The created project object.
    """
    new_project = Project(

        **data.model_dump(),
        owner_id=owner_id
    )

    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)
    
    return new_project


async def get_project_by_id(project_id: UUID, db: AsyncSession) -> Optional[Project]:
    """
    Get a project by its ID.

        Args:
            project_id (UUID): The ID of the project.
            db (AsyncSession): The database session.

        Returns:
            Optional[Project]: The project object if found, otherwise None.
    """
    query = select(Project).where(Project.id == project_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_user_projects(owner_id: UUID, db: AsyncSession) -> List[Project]:
    """
    Get all projects owned by a specific user.

        Args:
            owner_id (UUID): The ID of the user.
            db (AsyncSession): The database session.

        Returns:
            List[Project]: A list of projects owned by the user.
    """
    query = select(Project).where(Project.owner_id == owner_id)
    result = await db.execute(query)
    return result.scalars().all()


async def update_project(project_id: UUID, data: ProjectUpdate, db: AsyncSession) -> Optional[Project]:
    """
    Update an existing project.

        Args:
            project_id (UUID): The ID of the project to update.
            data (ProjectUpdate): The new data for the project.
            db (AsyncSession): The database session.

        Returns:
            Optional[Project]: The updated project object if found, otherwise None.
    """
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if project:
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(project, key, value)
        await db.commit()
        await db.refresh(project)
        return project
    

async def delete_project(project_id: UUID, db: AsyncSession) -> bool:
    """
    Delete a project by its ID.

        Args:
            project_id (UUID): The ID of the project to delete.
            db (AsyncSession): The database session.

        Returns:
            bool: True if the project was deleted, otherwise False.
    """
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    
    if not project:
        return False
    
    await db.execute(delete(Project).where(Project.id == project_id))
    await db.commit()
    
    return True