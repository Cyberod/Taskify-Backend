# New file for member management
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.db.session import get_db
from app.project.services import member_service
from app.project.dependencies.project_dependencies import require_project_member, require_user_management_permission

router = APIRouter(prefix="/projects", tags=["Project Members"])

@router.get("/{project_id}/members")
async def get_project_members(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_project_member)  # Must be project member to see members
):
    """
    Get all members of a specific project.
        Args:
            project_id (UUID): The ID of the project.
            db (AsyncSession): The database session.
            current_user: The currently authenticated user.
        Returns:
            List[ProjectMemberWithUser]: List of project members with user info.
    """
    return await member_service.get_project_members(project_id, db)



@router.delete("/{project_id}/members/{member_id}")
async def remove_project_member(
    project_id: UUID,
    member_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_user_management_permission)  # Must be admin/owner
):
    """
    Remove a member from a project.
        Args:
            project_id (UUID): The ID of the project.
            member_id (UUID): The ID of the member to remove.
            db (AsyncSession): The database session.
            current_user: The currently authenticated user with permission to manage members.
        Returns:
            dict: Confirmation message.
    """
    success = await member_service.remove_project_member(member_id, db)
    return {"message": "Member removed successfully"}
