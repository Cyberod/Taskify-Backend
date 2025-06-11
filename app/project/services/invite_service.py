import secrets
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.project.models.invite_models import ProjectInvite, InviteStatus
from app.project.models.member_models import ProjectMember
from app.project.models.project_models import ProjectRole
from app.user.models.user_models import User
from app.project.services.project_service import get_project_by_id
from app.auth.utils.email_sender import send_invite_email, get_user_by_email
from app.core.config import settings


async def create_project_invite(project_id: str, email: str, db: AsyncSession) -> ProjectInvite:
    """
    Create a new project invite.

        Args:
            project_id (str): The ID of the project.
            email (str): The email address to invite.
            db (AsyncSession): The database session.

        Returns:
            ProjectInvite: The created project invite object.
    """
    # Check if the project exists
    project = await get_project_by_id(project_id, db)
    if not project:
        raise ValueError("Project not found")

    # Check if user is already a member of this project
    user = await get_user_by_email(email, db)
    if user:
        # Check if user is project owner
        if project.owner_id == user.id:
            raise ValueError("Cannot invite project owner - they already have access")
        
        # Check if user is already a member
        existing_member_query = select(ProjectMember).where(
            ProjectMember.project_id == project.id,
            ProjectMember.user_id == user.id
        )
        existing_member_result = await db.execute(existing_member_query)
        existing_member = existing_member_result.scalar_one_or_none()
        
        if existing_member:
            raise ValueError("User is already a member of this project")

    # Check if there's already a pending invite for this email
    existing_invite_query = select(ProjectInvite).where(
        ProjectInvite.project_id == project.id,
        ProjectInvite.email == email,
        ProjectInvite.status == InviteStatus.PENDING
    )
    existing_invite_result = await db.execute(existing_invite_query)
    existing_invite = existing_invite_result.scalar_one_or_none()
    
    if existing_invite:
        raise ValueError("There is already a pending invite for this email")

    # Generate a unique token for the invite
    token = secrets.token_urlsafe(32)

    # Create the invite
    invite = ProjectInvite(
        project_id=project.id,
        email=email,
        token=token,
        status=InviteStatus.PENDING,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.INVITE_EXPIRATION_DAYS)
    )

    db.add(invite)
    await db.commit()
    await db.refresh(invite)

    # Send the invite email
    await send_invite_email(email_to=email, token=token)

    return invite


async def get_invite_by_token(token: str, db: AsyncSession) -> ProjectInvite | None:
    """
    Retrieve a project invite by its token.

        Args:
            token (str): The token of the invite.
            db (AsyncSession): The database session.

        Returns:
            ProjectInvite | None: The project invite object if found, otherwise None.
    """
    query = select(ProjectInvite).where(ProjectInvite.token == token)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def accept_project_invite(token: str, user_id: str, db: AsyncSession) -> dict:
    """
    Accept a project invite and create a ProjectMember record.

        Args:
            token (str): The token of the invite.
            user_id (str): The ID of the user accepting the invite.
            db (AsyncSession): The database session.

        Returns:
            dict: Success message with project and member info.
    """
    invite = await get_invite_by_token(token, db)
    if not invite:
        raise ValueError("Invite not found")

    # Check if the invite has expired
    if invite.expires_at < datetime.now(timezone.utc):
        invite.status = InviteStatus.EXPIRED
        await db.commit()
        raise ValueError("Invite has expired")

    # Check if invite is already processed
    if invite.status != InviteStatus.PENDING:
        raise ValueError(f"Invite already {invite.status.value}")

    # Get the user accepting the invite
    user_query = select(User).where(User.id == user_id)
    user_result = await db.execute(user_query)
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise ValueError("User not found")

    # Verify the invite email matches the user's email
    if user.email.lower() != invite.email.lower():
        raise ValueError("This invite was sent to a different email address")

    # Check if user is already a member (double-check)
    existing_member_query = select(ProjectMember).where(
        ProjectMember.project_id == invite.project_id,
        ProjectMember.user_id == user_id
    )
    existing_member_result = await db.execute(existing_member_query)
    existing_member = existing_member_result.scalar_one_or_none()
    
    if existing_member:
        # Update invite status but don't create duplicate member
        invite.status = InviteStatus.ACCEPTED
        await db.commit()
        raise ValueError("You are already a member of this project")

    # Create the ProjectMember record
    project_member = ProjectMember(
        project_id=invite.project_id,
        user_id=user_id,
        role=ProjectRole.MEMBER  # Default role for invited users
    )
    
    db.add(project_member)

    # Update invite status
    invite.status = InviteStatus.ACCEPTED
    
    await db.commit()
    await db.refresh(project_member)
    await db.refresh(invite)

    # Get project info for response
    project = await get_project_by_id(invite.project_id, db)

    return {
        "message": "Successfully joined the project",
        "project": {
            "id": str(project.id),
            "name": project.name,
            "description": project.description
        },
        "role": project_member.role.value,
        "joined_at": project_member.joined_at
    }


async def decline_project_invite(token: str, db: AsyncSession) -> ProjectInvite:
    """
    Decline a project invite.

        Args:
            token (str): The token of the invite.
            db (AsyncSession): The database session.

        Returns:
            ProjectInvite: The updated project invite object.
    """
    invite = await get_invite_by_token(token, db)
    if not invite:
        raise ValueError("Invite not found")

    if invite.status != InviteStatus.PENDING:
        raise ValueError(f"Invite already {invite.status.value}")

    invite.status = InviteStatus.REJECTED
    await db.commit()
    await db.refresh(invite)

    return invite


async def get_project_invites(project_id: str, db: AsyncSession) -> list[ProjectInvite]:
    """
    Get all invites for a specific project.

        Args:
            project_id (str): The ID of the project.
            db (AsyncSession): The database session.

        Returns:
            list[ProjectInvite]: List of project invites.
    """
    query = select(ProjectInvite).where(ProjectInvite.project_id == project_id)
    result = await db.execute(query)
    return result.scalars().all()


async def cancel_project_invite(invite_id: str, db: AsyncSession) -> bool:
    """
    Cancel a pending project invite.

        Args:
            invite_id (str): The ID of the invite to cancel.
            db (AsyncSession): The database session.

        Returns:
            bool: True if cancelled successfully.
    """
    invite_query = select(ProjectInvite).where(ProjectInvite.id == invite_id)
    invite_result = await db.execute(invite_query)
    invite = invite_result.scalar_one_or_none()
    
    if not invite:
        raise ValueError("Invite not found")
    
    if invite.status != InviteStatus.PENDING:
        raise ValueError("Can only cancel pending invites")
    
    invite.status = InviteStatus.EXPIRED  # Mark as expired instead of deleting
    await db.commit()
    
    return True
