from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.project.models.member_models import ProjectMember
from app.project.schemas.member_schemas import ProjectMemberUpdate, ProjectMemberWithUser
from app.user.models.user_models import User


async def get_project_members(project_id: UUID, db: AsyncSession) -> List[ProjectMemberWithUser]:
    """
    Get all members of a specific project with user details.

        Args:
            project_id (UUID): The ID of the project.
            db (AsyncSession): The database session.

        Returns:
            List[ProjectMemberWithUser]: List of project members with user info.
    """
    query = select(ProjectMember, User).join(User).where(ProjectMember.project_id == project_id)
    result = await db.execute(query)
    
    members_with_users = []
    for member, user in result.all():
        member_data = ProjectMemberWithUser(
            id=member.id,
            project_id=member.project_id,
            user_id=member.user_id,
            role=member.role,
            joined_at=member.joined_at,
            user_email=user.email,
            user_avatar_url=user.avatar_url
        )
        members_with_users.append(member_data)
    
    return members_with_users


async def update_member_role(
    member_id: UUID, 
    role_data: ProjectMemberUpdate, 
    db: AsyncSession
) -> ProjectMember:
    """
    Update a project member's role.

        Args:
            member_id (UUID): The ID of the project member.
            role_data (ProjectMemberUpdate): The new role data.
            db (AsyncSession): The database session.

        Returns:
            ProjectMember: The updated project member.
    """
    query = select(ProjectMember).where(ProjectMember.id == member_id)
    result = await db.execute(query)
    member = result.scalar_one_or_none()
    
    if not member:
        raise ValueError("Project member not found")
    
    member.role = role_data.role
    await db.commit()
    await db.refresh(member)
    
    return member


async def remove_project_member(member_id: UUID, db: AsyncSession) -> bool:
    """
    Remove a member from a project.

        Args:
            member_id (UUID): The ID of the project member to remove.
            db (AsyncSession): The database session.

        Returns:
            bool: True if removed successfully.
    """
    query = select(ProjectMember).where(ProjectMember.id == member_id)
    result = await db.execute(query)
    member = result.scalar_one_or_none()
    
    if not member:
        raise ValueError("Project member not found")
    
    await db.delete(member)
    await db.commit()
    
    return True


async def get_user_projects_as_member(user_id: UUID, db: AsyncSession) -> List[ProjectMember]:
    """
    Get all projects where the user is a member (not owner).

        Args:
            user_id (UUID): The ID of the user.
            db (AsyncSession): The database session.

        Returns:
            List[ProjectMember]: List of project memberships.
    """
    query = select(ProjectMember).where(ProjectMember.user_id == user_id)
    result = await db.execute(query)
    return result.scalars().all()
