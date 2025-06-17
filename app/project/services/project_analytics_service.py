from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from fastapi import HTTPException, status

from app.project.models.project_models import Project
from app.project.models.member_models import ProjectMember
from app.task.models.task_models import Task, TaskStatus, TaskPriority
from app.user.models.user_models import User
from app.project.schemas.project_analytics_schemas import (
    ProjectCompletionStats,
    TaskStatusCount,
    ProjectHealthStatus,
    UserContribution,
    ProjectAnalyticsDashboard,
    ProjectHealthStats
)
from app.project.utils.permissions import require_project_permission, ProjectPermission


def calculate_project_health(
    completion_percentage: float,
    deadline: Optional[datetime],
    current_time: Optional[datetime] = None
) -> tuple[ProjectHealthStatus, Optional[int], str]:
    """
    Calculate project health status based on completion and deadline.
    
    Args:
        completion_percentage: Current project completion percentage
        deadline: Project deadline
        current_time: Current time (defaults to now)
        
    Returns:
        Tuple of (health_status, days_until_deadline, color_code)
    """
    if current_time is None:
        current_time = datetime.now(timezone.utc)
    
    # If project is completed
    if completion_percentage >= 100:
        return ProjectHealthStatus.COMPLETED, None, "#10B981"  # Green
    
    # If no deadline is set
    if deadline is None:
        return ProjectHealthStatus.ON_TRACK, None, "#3B82F6"  # Blue
    
    # Calculate days until deadline
    days_until_deadline = (deadline - current_time).days
    
    # Determine health status based on completion vs time remaining
    if days_until_deadline < 0:
        # Past deadline
        return ProjectHealthStatus.OVERDUE, days_until_deadline, "#EF4444"  # Red
    elif days_until_deadline <= 7 and completion_percentage < 80:
        # Less than a week and not 80% complete
        return ProjectHealthStatus.AT_RISK, days_until_deadline, "#F59E0B"  # Orange
    elif days_until_deadline <= 14 and completion_percentage < 50:
        # Less than two weeks and not 50% complete
        return ProjectHealthStatus.AT_RISK, days_until_deadline, "#F59E0B"  # Orange
    else:
        # On track
        return ProjectHealthStatus.ON_TRACK, days_until_deadline, "#10B981"  # Green


async def get_project_completion_stats(
    project_id: UUID,
    db: AsyncSession,
    current_user_id: UUID
) -> ProjectCompletionStats:
    """
    Get detailed project completion statistics.
    
    Args:
        project_id: The project ID
        db: Database session
        current_user_id: Current user ID for permission checking
        
    Returns:
        ProjectCompletionStats object
    """
    # Check permissions
    await require_project_permission(
        current_user_id,
        project_id,
        ProjectPermission.VIEW_ALL_TASKS,
        db
    )
    
    # Get project
    project_query = select(Project).where(Project.id == project_id)
    project_result = await db.execute(project_query)
    project = project_result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Get task counts by status
    task_counts_query = select(
        Task.status,
        func.count(Task.id).label('count')
    ).where(Task.project_id == project_id).group_by(Task.status)
    
    task_counts_result = await db.execute(task_counts_query)
    task_counts_raw = task_counts_result.all()
    
    # Initialize task counts
    task_counts = TaskStatusCount()
    total_tasks = 0
    
    for status, count in task_counts_raw:
        total_tasks += count
        if status == TaskStatus.NOT_STARTED:
            task_counts.not_started = count
        elif status == TaskStatus.IN_PROGRESS:
            task_counts.in_progress = count
        elif status == TaskStatus.BLOCKED:
            task_counts.blocked = count
        elif status == TaskStatus.COMPLETED:
            task_counts.completed = count
    
    task_counts.total = total_tasks
    
    # Calculate health status
    health_status, days_until_deadline, color_code = calculate_project_health(
        project.completion_percentage,
        project.deadline
    )
    
    return ProjectCompletionStats(
        project_id=project.id,
        name=project.name,
        description=project.description,
        completion_percentage=project.completion_percentage,
        task_counts=task_counts,
        days_until_deadline=days_until_deadline,
        deadline=project.deadline,
        health_status=health_status,
        created_at=project.created_at,
        updated_at=project.updated_at
    )


async def get_project_health_stats(
    project_id: UUID,
    db: AsyncSession,
    current_user_id: UUID
) -> ProjectHealthStats:
    """
    Get project health statistics.
    
        Args:
            project_id: The project ID
            db: Database session
            current_user_id: Current user ID for permission checking
            
        Returns:
            ProjectHealthStats object
    """
    # Check permissions
    await require_project_permission(
        current_user_id,
        project_id,
        ProjectPermission.VIEW_ALL_TASKS,
        db
    )
    
    # Get project
    project_query = select(Project).where(Project.id == project_id)
    project_result = await db.execute(project_query)
    project = project_result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Calculate health status
    health_status, days_until_deadline, color_code = calculate_project_health(
        project.completion_percentage,
        project.deadline
    )
    
    return ProjectHealthStats(
        project_id=project.id,
        name=project.name,
        health_status=health_status,
        completion_percentage=project.completion_percentage,
        days_until_deadline=days_until_deadline,
        deadline=project.deadline,
        color_code=color_code
    )


async def get_user_project_contributions(
    project_id: UUID,
    db: AsyncSession,
    current_user_id: UUID
) -> List[UserContribution]:
    """
    Get user contribution metrics for a project.
    
        Args:
            project_id: The project ID
            db: Database session
            current_user_id: Current user ID for permission checking
            
        Returns:
            List of UserContribution objects
    """
    # Check permissions - only admins/owners can see all user contributions
    await require_project_permission(
        current_user_id,
        project_id,
        ProjectPermission.VIEW_ALL_TASKS,
        db
    )
    
    # Get all users who have tasks in this project (assigned or created)
    users_query = select(User).join(Task, Task.assignee_id == User.id).where(
        Task.project_id == project_id
    ).distinct()
    
    users_result = await db.execute(users_query)
    users = users_result.scalars().all()
    
    contributions = []
    
    for user in users:
        # Get user's task counts
        assigned_tasks_query = select(func.count(Task.id)).where(
            and_(Task.project_id == project_id, Task.assignee_id == user.id)
        )
        assigned_count = (await db.execute(assigned_tasks_query)).scalar() or 0
        
        completed_tasks_query = select(func.count(Task.id)).where(
            and_(
                Task.project_id == project_id,
                Task.assignee_id == user.id,
                Task.status == TaskStatus.COMPLETED
            )
        )
        completed_count = (await db.execute(completed_tasks_query)).scalar() or 0
        
        # Get tasks by priority
        priority_query = select(
            Task.priority,
            func.count(Task.id).label('count')
        ).where(
            and_(Task.project_id == project_id, Task.assignee_id == user.id)
        ).group_by(Task.priority)
        
        priority_result = await db.execute(priority_query)
        tasks_by_priority = {
            priority.value: count for priority, count in priority_result.all()
        }
        
        # Calculate completion percentage
        completion_percentage = (
            (completed_count / assigned_count * 100) if assigned_count > 0 else 0
        )
        
        contributions.append(UserContribution(
            user_id=user.id,
            user_email=user.email,
            user_avatar_url=user.avatar_url,
            assigned_tasks_count=assigned_count,
            completed_tasks_count=completed_count,
            completion_percentage=round(completion_percentage, 2),
            tasks_by_priority=tasks_by_priority
        ))
    
    return contributions


async def get_project_analytics_dashboard(
    project_id: UUID,
    db: AsyncSession,
    current_user_id: UUID
) -> ProjectAnalyticsDashboard:
    """
    Get comprehensive project analytics for dashboard.
    
    Args:
        project_id: The project ID
        db: Database session
        current_user_id: Current user ID for permission checking
        
    Returns:
        ProjectAnalyticsDashboard object
    """
    # Get project stats and user contributions
    project_stats = await get_project_completion_stats(project_id, db, current_user_id)
    user_contributions = await get_user_project_contributions(project_id, db, current_user_id)
    
    return ProjectAnalyticsDashboard(
        project_stats=project_stats,
        user_contributions=user_contributions,
        recent_activity=[]  # We can implement this later
    )
