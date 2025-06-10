import secrets
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.project.models.invite_models import ProjectInvite, InviteStatus
from app.user.models.user_models import User
from app.project.services.project_services import get_project_by_id
from app.auth.utils.email_sender import send_invite_email
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


async def accept_project_invite(token: str, user_id: str, db: AsyncSession) -> ProjectInvite | None:
    """
    Accept a project invite.

        Args:
            token (str): The token of the invite.
            user_id (str): The ID of the user accepting the invite.
            db (AsyncSession): The database session.

        Returns:
            ProjectInvite: The updated project invite object or none if expired or declined.
    """
    invite = await get_invite_by_token(token, db)
    if not invite:
        raise ValueError("Invite not found")

    # Check if the invite has expired
    if invite.expires_at < datetime.now(timezone.utc):
        invite.status = InviteStatus.EXPIRED
        await db.commit()
        raise ValueError("Invite has expired")

    # check if invite is already Processed
    if invite.status != InviteStatus.PENDING:
        raise  ValueError(f"Invite already {invite.status.value}")
    

    # Accept the invite
    invite.status = InviteStatus.ACCEPTED
    await db.commit()
    await db.refresh(invite)

    return invite


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