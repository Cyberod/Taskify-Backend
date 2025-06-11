from typing import Annotated
from uuid import UUID
from fastapi import Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.user.dependencies.user_dependencies import get_current_user
from app.user.models.user_models import User
from app.project.utils.permissions import (
    ProjectPermission,
    require_project_permission,
)


async def require_project_owner(
    project_id: Annotated[UUID, Path()],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Require user to be project owner"""
    await require_project_permission(
        current_user.id, project_id, ProjectPermission.DELETE_PROJECT, db
    )
    return current_user


async def require_project_admin(
    project_id: Annotated[UUID, Path()],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Require user to be project admin or owner"""
    await require_project_permission(
        current_user.id, project_id, ProjectPermission.EDIT_PROJECT, db
    )
    return current_user


async def require_project_member(
    project_id: Annotated[UUID, Path()],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Require user to be project member (any role)"""
    await require_project_permission(
        current_user.id, project_id, ProjectPermission.VIEW_ALL_TASKS, db
    )
    return current_user


async def require_task_creation_permission(
    project_id: Annotated[UUID, Path()],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Require user to be able to create tasks"""
    await require_project_permission(
        current_user.id, project_id, ProjectPermission.CREATE_TASKS, db
    )
    return current_user


async def require_user_management_permission(
    project_id: Annotated[UUID, Path()],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Require user to be able to manage project users"""
    await require_project_permission(
        current_user.id, project_id, ProjectPermission.INVITE_USERS, db
    )
    return current_user
