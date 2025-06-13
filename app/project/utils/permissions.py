from enum import Enum
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.project.models.project_models import Project, ProjectRole
from app.project.models.member_models import ProjectMember



class ProjectPermission(Enum):
    """Define all possible project permissions"""
    # Project Management
    DELETE_PROJECT = "delete_project"
    EDIT_PROJECT = "edit_project"
    ARCHIVE_PROJECT = "archive_project"
    
    # User Management
    INVITE_USERS = "invite_users"
    REMOVE_USERS = "remove_users"
    CHANGE_USER_ROLES = "change_user_roles"
    
    # Task Management
    CREATE_TASKS = "create_tasks"
    ASSIGN_TASKS = "assign_tasks"
    DELETE_ANY_TASK = "delete_any_task"
    EDIT_ANY_TASK = "edit_any_task"
    
    # Task Interaction
    VIEW_ALL_TASKS = "view_all_tasks"
    CLAIM_TASKS = "claim_tasks"
    EDIT_OWN_TASKS = "edit_own_tasks"
    COMMENT_ON_TASKS = "comment_on_tasks"


# Permission matrix - defines what each role can do
ROLE_PERMISSIONS = {
    ProjectRole.OWNER: {
        # Project Management
        ProjectPermission.DELETE_PROJECT,
        ProjectPermission.EDIT_PROJECT,
        ProjectPermission.ARCHIVE_PROJECT,
        
        # User Management
        ProjectPermission.INVITE_USERS,
        ProjectPermission.REMOVE_USERS,
        ProjectPermission.CHANGE_USER_ROLES,
        
        # Task Management
        ProjectPermission.CREATE_TASKS,
        ProjectPermission.ASSIGN_TASKS,
        ProjectPermission.DELETE_ANY_TASK,
        ProjectPermission.EDIT_ANY_TASK,
        
        # Task Interaction
        ProjectPermission.VIEW_ALL_TASKS,
        ProjectPermission.CLAIM_TASKS,
        ProjectPermission.EDIT_OWN_TASKS,
        ProjectPermission.COMMENT_ON_TASKS,
    },
    
    ProjectRole.ADMIN: {
        # Project Management (no delete)
        ProjectPermission.EDIT_PROJECT,
        ProjectPermission.ARCHIVE_PROJECT,
        
        # User Management
        ProjectPermission.INVITE_USERS,
        ProjectPermission.REMOVE_USERS,
        ProjectPermission.CHANGE_USER_ROLES,
        
        # Task Management
        ProjectPermission.CREATE_TASKS,
        ProjectPermission.ASSIGN_TASKS,
        ProjectPermission.DELETE_ANY_TASK,
        ProjectPermission.EDIT_ANY_TASK,
        
        # Task Interaction
        ProjectPermission.VIEW_ALL_TASKS,
        ProjectPermission.CLAIM_TASKS,
        ProjectPermission.EDIT_OWN_TASKS,
        ProjectPermission.COMMENT_ON_TASKS,
    },
    
    ProjectRole.MEMBER: {
        # Task Management (limited)
        ProjectPermission.CREATE_TASKS,
        
        # Task Interaction
        ProjectPermission.VIEW_ALL_TASKS,
        ProjectPermission.CLAIM_TASKS,
        ProjectPermission.EDIT_OWN_TASKS,
        ProjectPermission.COMMENT_ON_TASKS,
    },
    
    ProjectRole.GUEST: {
        # Task Interaction (read-only mostly)
        ProjectPermission.VIEW_ALL_TASKS,
        ProjectPermission.EDIT_OWN_TASKS,
        ProjectPermission.COMMENT_ON_TASKS,
    }
}


async def get_user_project_role(
    user_id: UUID, 
    project_id: UUID, 
    db: AsyncSession
) -> Optional[ProjectRole]:
    """
    Get a user's role in a specific project.
    
    Args:
        user_id: The user's ID
        project_id: The project's ID
        db: Database session
        
    Returns:
        ProjectRole if user is in project, None otherwise
    """
    # Check if user is the project owner
    project_query = select(Project).where(
        Project.id == project_id,
        Project.owner_id == user_id
    )
    project_result = await db.execute(project_query)
    project = project_result.scalar_one_or_none()
    
    if project:
        return ProjectRole.OWNER
    
    # Check if user is a project member
    member_query = select(ProjectMember).where(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id
    )
    member_result = await db.execute(member_query)
    member = member_result.scalar_one_or_none()
    
    if member:
        return member.role
    
    return None


async def user_has_project_permission(
    user_id: UUID,
    project_id: UUID,
    permission: ProjectPermission,
    db: AsyncSession
) -> bool:
    """
    Check if a user has a specific permission in a project.
    
    Args:
        user_id: The user's ID
        project_id: The project's ID
        permission: The permission to check
        db: Database session
        
    Returns:
        True if user has permission, False otherwise
    """
    user_role = await get_user_project_role(user_id, project_id, db)
    
    if not user_role:
        return False
    
    return permission in ROLE_PERMISSIONS.get(user_role, set())


async def require_project_permission(
    user_id: UUID,
    project_id: UUID,
    permission: ProjectPermission,
    db: AsyncSession
) -> None:
    """
    Require a user to have a specific permission in a project.
    Raises HTTPException if permission is denied.
    
    Args:
        user_id: The user's ID
        project_id: The project's ID
        permission: The required permission
        db: Database session
        
    Raises:
        HTTPException: If user doesn't have permission
    """
    has_permission = await user_has_project_permission(
        user_id, project_id, permission, db
    )
    
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You don't have permission to {permission.value} in this project"
        )
    


async def get_user_accessible_projects(
    user_id: UUID,
    db: AsyncSession
) -> list[Project]:
    """
    Get all projects a user has access to (owns or is a member of).
    
    Args:
        user_id: The user's ID
        db: Database session
        
    Returns:
        List of projects the user can access
    """
    # Get projects user owns
    owned_projects_query = select(Project).where(Project.owner_id == user_id)
    owned_result = await db.execute(owned_projects_query)
    owned_projects = owned_result.scalars().all()
    
    # Get projects user is a member of
    member_projects_query = select(Project).join(ProjectMember).where(
        ProjectMember.user_id == user_id
    )
    member_result = await db.execute(member_projects_query)
    member_projects = member_result.scalars().all()
    
    # Combine and deduplicate
    all_projects = list(owned_projects) + list(member_projects)
    unique_projects = {project.id: project for project in all_projects}
    
    return list(unique_projects.values())


# Convenience functions for common permission checks
async def can_manage_project(user_id: UUID, project_id: UUID, db: AsyncSession) -> bool:
    """Check if user can edit/manage project settings"""
    return await user_has_project_permission(
        user_id, project_id, ProjectPermission.EDIT_PROJECT, db
    )


async def can_manage_users(user_id: UUID, project_id: UUID, db: AsyncSession) -> bool:
    """Check if user can invite/remove users"""
    return await user_has_project_permission(
        user_id, project_id, ProjectPermission.INVITE_USERS, db
    )


async def can_manage_tasks(user_id: UUID, project_id: UUID, db: AsyncSession) -> bool:
    """Check if user can assign tasks to others"""
    return await user_has_project_permission(
        user_id, project_id, ProjectPermission.ASSIGN_TASKS, db
    )


async def can_create_tasks(user_id: UUID, project_id: UUID, db: AsyncSession) -> bool:
    """Check if user can create tasks"""
    return await user_has_project_permission(
        user_id, project_id, ProjectPermission.CREATE_TASKS, db
    )
