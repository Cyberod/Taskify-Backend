from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

## Added some other fields here i think would be interesting to be shown in the Dashboard or analytics page


class ProjectHealthStatus(str, Enum):
    """Project health status based on deadline and completion"""
    ON_TRACK = "ON_TRACK"
    AT_RISK = "AT_RISK" # When the project is at risk of soon being overdue
    OVERDUE = "OVERDUE" # When the project is overdue and not yet completed
    COMPLETED = "COMPLETED" #when the project has been completed



class TaskStatusCount(BaseModel):
    """count of tasks by sttus"""
    not_started: int = 0
    in_progress: int = 0
    blocked: int = 0
    completed: int = 0
    total: int = 0


class UserContribution(BaseModel):
    """User contribution metrics for a Project"""
    user_id: UUID
    user_email: str
    user_avatar_url: Optional[str] = None
    assigned_tasks_count: int
    completed_tasks_count: int
    completion_percentage: float
    tasks_by_priority: dict = Field(default_factory=dict)

class ProjectCompletionStats(BaseModel):
    """Detailed Project Completion Stats"""
    project_id: UUID
    name: str
    description: Optional[str] = None
    completion_percentage: float
    tasks_count: TaskStatusCount
    days_until_deadline: Optional[int] = None
    deadline: Optional[datetime] = None
    health_status: ProjectHealthStatus
    created_at: datetime
    updated_at: datetime


class ProjectHealthStats(BaseModel):
    """Project Health Statistics"""
    project_id: UUID
    name: str
    health_status: ProjectHealthStatus
    completion_percentage: float
    days_until_deadline: Optional[int] = None
    deadline: Optional[datetime] = None
    color_code: str #Hex color code representing health status


class ProjectAnalyticsDashboard:
    """Comprehensive project analytics for Dashboard"""
    project_stats: ProjectCompletionStats
    user_contribution: List[UserContribution]
    recent_activity: Optional[List] = None  # If you want, this can be done later @Goodluck



