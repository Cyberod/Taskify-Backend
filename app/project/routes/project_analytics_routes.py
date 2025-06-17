from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from app.db.session import get_db
from app.user.dependencies.user_dependencies import get_current_user
from app.user.models.user_models import User
from app.project.services import project_analytics_service
from app.project.schemas.project_analytics_schemas import (
    ProjectCompletionStats,
    ProjectHealthStats,
    UserContribution,
    ProjectAnalyticsDashboard
)

router = APIRouter(prefix="/projects", tags=["Project Analytics"])


@router.get("/{project_id}/analytics/completion", response_model=ProjectCompletionStats)
async def get_project_completion_stats(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed project completion statistics.
    
    Args:
        project_id: The project ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        ProjectCompletionStats: Detailed completion statistics
    """
    return await project_analytics_service.get_project_completion_stats(
        project_id, db, current_user.id
    )


@router.get("/{project_id}/analytics/health", response_model=ProjectHealthStats)
async def get_project_health_stats(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get project health statistics with color coding.
    
    Args:
        project_id: The project ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        ProjectHealthStats: Health status with color coding
    """
    return await project_analytics_service.get_project_health_stats(
        project_id, db, current_user.id
    )


@router.get("/{project_id}/analytics/contributions", response_model=List[UserContribution])
async def get_user_contributions(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user contribution metrics for a project.
    
    Args:
        project_id: The project ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List[UserContribution]: User contribution metrics
    """
    return await project_analytics_service.get_user_project_contributions(
        project_id, db, current_user.id
    )


@router.get("/{project_id}/analytics/dashboard", response_model=ProjectAnalyticsDashboard)
async def get_project_analytics_dashboard(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive project analytics for dashboard view.
    
    Args:
        project_id: The project ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        ProjectAnalyticsDashboard: Complete analytics data
    """
    return await project_analytics_service.get_project_analytics_dashboard(
        project_id, db, current_user.id
    )
