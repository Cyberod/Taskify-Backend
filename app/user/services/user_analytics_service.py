from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from fastapi import HTTPException, status

from app.user.models.user_models import User, UserRole
from app.project.models.project_models import Project, ProjectRole, ProjectStatus
from app.project.models.member_models import ProjectMember
from app.task.models.task_models import Task, TaskStatus
from app.user.schemas.user_analytics_schemas import (
    UserOverallMetrics,
    UserProjectSummary,
    ProjectUserMetrics,
    TeamProductivityMetrics
)
from app.project.schemas.project_analytics_schemas import UserContribution, ProjectHealthStatus
from app.project.services.project_analytics_service import calculate_project_health
from app.project.utils.permissions import get_user_project_role



async def get_user_overall_metrics(
    user_id: UUID,
    db: AsyncSession,
    requesting_user_id: UUID
) -> UserOverallMetrics:
    """
    Get overall metrics for a specific user across all their projects.
    
    Args:
        user_id: Target user ID
        db: Database session
        requesting_user_id: ID of user making the request
        
    Returns:
        UserOverallMetrics object
    """
    # Check if requesting user can view this data
    # Users can view their own metrics, admins can view anyone's
    requesting_user_query = select(User).where(User.id == requesting_user_id)
    requesting_user_result = await db.execute(requesting_user_query)
    requesting_user = requesting_user_result.scalar_one_or_none()
    
    if not requesting_user:
        raise HTTPException(status_code=404, detail="Requesting user not found")
    

    # Check if requesting user has completed onboarding (except for viewing own data)
    if requesting_user_id != user_id:
        if requesting_user.is_verified and not requesting_user.onboarding_completed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Complete onboarding to access this feature"
            )

    # Allow if viewing own data or if admin
    if user_id != requesting_user_id and requesting_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own metrics"
        )
    
    # Get target user
    user_query = select(User).where(User.id == user_id)
    user_result = await db.execute(user_query)
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get projects where user is owner
    owned_projects_query = select(func.count(Project.id)).where(Project.owner_id == user_id)
    projects_owned = (await db.execute(owned_projects_query)).scalar() or 0
    
    # Get projects where user is member
    member_projects_query = select(func.count(ProjectMember.id)).where(
        ProjectMember.user_id == user_id
    )
    projects_as_member = (await db.execute(member_projects_query)).scalar() or 0
    
    total_projects = projects_owned + projects_as_member
    
    # Get task statistics
    total_assigned_query = select(func.count(Task.id)).where(Task.assignee_id == user_id)
    total_assigned_tasks = (await db.execute(total_assigned_query)).scalar() or 0
    
    completed_tasks_query = select(func.count(Task.id)).where(
        and_(Task.assignee_id == user_id, Task.status == TaskStatus.COMPLETED)
    )
    total_completed_tasks = (await db.execute(completed_tasks_query)).scalar() or 0
    
    overall_completion = (
        (total_completed_tasks / total_assigned_tasks * 100) 
        if total_assigned_tasks > 0 else 0
    )
    
    # Get project summaries
    project_summaries = await _get_user_project_summaries(user_id, db)
    
    return UserOverallMetrics(
        user_id=user.id,
        user_email=user.email,
        user_name=f"{user.first_name} {user.last_name}" if user.first_name and user.last_name else user.email,
        user_avatar_url=user.avatar_url,
        total_projects=total_projects,
        total_assigned_tasks=total_assigned_tasks,
        total_completed_tasks=total_completed_tasks,
        overall_completion_percentage=round(overall_completion, 2),
        projects_owned=projects_owned,
        projects_as_member=projects_as_member,
        project_summaries=project_summaries
    )


async def _get_user_project_summaries(user_id: UUID, db: AsyncSession) -> List[UserProjectSummary]:
    """Get summaries of all projects a user is involved in"""
    summaries = []
    
    # Get owned projects
    owned_projects_query = select(Project).where(Project.owner_id == user_id)
    owned_projects_result = await db.execute(owned_projects_query)
    owned_projects = owned_projects_result.scalars().all()
    
    for project in owned_projects:
        summary = await _create_project_summary(user_id, project, "OWNER", db)
        summaries.append(summary)
    
    # Get member projects
    member_projects_query = select(Project, ProjectMember.role).join(
        ProjectMember, Project.id == ProjectMember.project_id
    ).where(
        and_(
            ProjectMember.user_id == user_id,
            Project.owner_id != user_id  # Exclude projects where user is owner
        )
    )
    
    member_projects_result = await db.execute(member_projects_query)
    member_projects = member_projects_result.all()
    
    for project, role in member_projects:
        summary = await _create_project_summary(user_id, project, role, db)
        summaries.append(summary)
    
    return summaries


async def _create_project_summary(
    user_id: UUID, 
    project: Project, 
    role: str, 
    db: AsyncSession
) -> UserProjectSummary:
    """Create a project summary for a user"""
    # Get user's task counts for this project
    assigned_tasks_query = select(func.count(Task.id)).where(
        and_(Task.project_id == project.id, Task.assignee_id == user_id)
    )
    assigned_tasks = (await db.execute(assigned_tasks_query)).scalar() or 0
    
    completed_tasks_query = select(func.count(Task.id)).where(
        and_(
            Task.project_id == project.id,
            Task.assignee_id == user_id,
            Task.status == TaskStatus.COMPLETED
        )
    )
    completed_tasks = (await db.execute(completed_tasks_query)).scalar() or 0
    
    completion_percentage = (
        (completed_tasks / assigned_tasks * 100) if assigned_tasks > 0 else 0
    )
    
    # Calculate project health
    health_status, _, _ = calculate_project_health(
        project.completion_percentage,
        project.deadline
    )
    
    return UserProjectSummary(
        project_id=project.id,
        project_name=project.name,
        project_health=health_status,
        user_role=role,
        assigned_tasks=assigned_tasks,
        completed_tasks=completed_tasks,
        completion_percentage=round(completion_percentage, 2),
        project_completion_percentage=project.completion_percentage
    )


async def get_team_productivity_metrics(
    db: AsyncSession,
    current_user_id: UUID
) -> TeamProductivityMetrics:
    """
    Get overall team productivity metrics (admin only).
    
    Args:
        db: Database session
        current_user_id: Current user ID
        
    Returns:
        TeamProductivityMetrics object
    """
    # Check if user is admin
    user_query = select(User).where(User.id == current_user_id)
    user_result = await db.execute(user_query)
    user = user_result.scalar_one_or_none()
    
    if not user or user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    # Add onboarding check after admin validation
    if user.is_verified and not user.onboarding_completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Complete onboarding to access admin features"
        )

    
    # Get basic counts
    active_projects_query = select(func.count(Project.id)).where(
        Project.status == ProjectStatus.ACTIVE
    )
    total_active_projects = (await db.execute(active_projects_query)).scalar() or 0
    
    total_users_query = select(func.count(User.id)).where(User.is_active == True)
    total_users = (await db.execute(total_users_query)).scalar() or 0
    
    total_tasks_query = select(func.count(Task.id))
    total_tasks = (await db.execute(total_tasks_query)).scalar() or 0
    
    completed_tasks_query = select(func.count(Task.id)).where(
        Task.status == TaskStatus.COMPLETED
    )
    completed_tasks = (await db.execute(completed_tasks_query)).scalar() or 0
    
    overall_productivity = (
        (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    )
    
    # Get project health counts
    projects_query = select(Project).where(Project.status == ProjectStatus.ACTIVE)
    projects_result = await db.execute(projects_query)
    projects = projects_result.scalars().all()
    
    on_track = at_risk = overdue = 0
    for project in projects:
        health_status, _, _ = calculate_project_health(
            project.completion_percentage,
            project.deadline
        )
        if health_status == ProjectHealthStatus.ON_TRACK:
            on_track += 1
        elif health_status == ProjectHealthStatus.AT_RISK:
            at_risk += 1
        elif health_status == ProjectHealthStatus.OVERDUE:
            overdue += 1
    
    # Get top contributors (users with highest completion rates)
    most_productive_users = await _get_top_contributors(db, limit=5)
    
    return TeamProductivityMetrics(
        total_active_projects=total_active_projects,
        total_users=total_users,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        overall_productivity=round(overall_productivity, 2),
        projects_on_track=on_track,
        projects_at_risk=at_risk,
        projects_overdue=overdue,
        most_productive_users=most_productive_users
    )


async def _get_top_contributors(db: AsyncSession, limit: int = 5) -> List[UserContribution]:
    """Get top contributing users across all projects"""
    # Get users with their task completion stats
    users_query = select(User).where(User.is_active == True)
    users_result = await db.execute(users_query)
    users = users_result.scalars().all()
    
    contributors = []
    
    for user in users:
        assigned_tasks_query = select(func.count(Task.id)).where(Task.assignee_id == user.id)
        assigned_count = (await db.execute(assigned_tasks_query)).scalar() or 0
        
        if assigned_count == 0:
            continue
        
        completed_tasks_query = select(func.count(Task.id)).where(
            and_(Task.assignee_id == user.id, Task.status == TaskStatus.COMPLETED)
        )
        completed_count = (await db.execute(completed_tasks_query)).scalar() or 0
        
        completion_percentage = (completed_count / assigned_count * 100)
        
        contributors.append(UserContribution(
            user_id=user.id,
            user_email=user.email,
            user_avatar_url=user.avatar_url,
            assigned_tasks_count=assigned_count,
            completed_tasks_count=completed_count,
            completion_percentage=round(completion_percentage, 2),
            tasks_by_priority={}
        ))
    
    # Sort by completion percentage and return top contributors
    contributors.sort(key=lambda x: x.completion_percentage, reverse=True)
    return contributors[:limit]