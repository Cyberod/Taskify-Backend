from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


from app.project.schemas.project_analytics_schemas import ProjectHealthStatus, UserContribution



class UserProjectSummary(BaseModel):
    """summary of user's involvement in a project"""
    project_id: UUID
    project_name: str
    project_health: ProjectHealthStatus
    user_role: str # Either owner, admin, Member or Guest
    assigned_tasks: int
    completed_tasks: int
    completion_percentage: float
    project_completion_percentage: float



class UserOverallMetrics(BaseModel):
    """Overall user metrics across all project"""
    user_id: UUID
    user_email: str
    user_avatar_url: Optional[str] = None
    total_projects: int
    total_assigned_tasks: int
    total_completed_tasks: int
    overall_completion_percentage: float
    projects_owned: int
    projects_as_member: int
    project_summaries: List[UserProjectSummary]


class ProjectUserMetrics(BaseModel):
    """Metrics for all users in a specific project"""
    project_id: UUID
    project_name: str
    project_completion: float
    project_health: ProjectHealthStatus
    user_contribution: List[UserContribution]
    top_contributors: List[UserContribution] = Field(default_factory=list)



class TeamProductivityMetrics(BaseModel):
    """Team Productivity metrics for admin"""
    total_active_projects: int
    total_users: int
    total_tasks: int
    completed_tasks: int
    overall_productivity: float
    projects_on_track: int
    projects_at_risk: int
    projects_overdue: int
    most_productive_users: List[UserContribution] = Field(default_factory=list)