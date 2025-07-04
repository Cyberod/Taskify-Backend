from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.db.session import get_db
from app.user.dependencies.user_dependencies import get_current_user
from app.user.models.user_models import User
from app.user.services import user_analytics_service
from app.user.schemas.user_analytics_schemas import (
    UserOverallMetrics,
    TeamProductivityMetrics
)

router = APIRouter(prefix="/users", tags=["User Analytics"])


@router.get("/me/analytics", response_model=UserOverallMetrics)
async def get_my_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get metrics for the current user.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        UserOverallMetrics: Current user's complete metrics
    """
    return await user_analytics_service.get_user_overall_metrics(
        current_user.id, db, current_user.id
    )




@router.get("/{user_id}/analytics", response_model=UserOverallMetrics)
async def get_user_metrics(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get overall metrics for a specific user.
    Users can view their own metrics, admins can view anyone's.
    
    Args:
        user_id: Target user ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        UserOverallMetrics: Complete user metrics
    """
    return await user_analytics_service.get_user_overall_metrics(
        user_id, db, current_user.id
    )



@router.get("/analytics/team", response_model=TeamProductivityMetrics)
async def get_team_productivity(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get overall team productivity metrics.
    Admin access only.
    
    Args:
        db: Database session
        current_user: Current authenticated user (must be admin)
        
    Returns:
        TeamProductivityMetrics: Team-wide productivity statistics
    """
    return await user_analytics_service.get_team_productivity_metrics(
        db, current_user.id
    )
