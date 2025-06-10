from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.user.dependencies.user_dependencies import get_current_user
from app.user.models.user_models import User
from app.project.services import invite_service as service
from app.project.schemas.invite_schemas import ProjectInviteCreate, AcceptInvite

router = APIRouter(prefix="/projects", tags=["Project Invites"])

# Send invite
@router.post("/{project_id}/invite", status_code=status.HTTP_201_CREATED)
async def send_project_invite(
    project_id: str,
    invite_data: ProjectInviteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Send a project invite to a user by email.
    
    Args:
        project_id (str): The ID of the project.
        invite_data (ProjectInviteCreate): The data for the invite.
        db (AsyncSession): The database session.
        current_user (User): The currently authenticated user.

    Returns:
        ProjectInviteRead: The created project invite object.
    """

    try:
        invite = await service.create_project_invite(project_id, invite_data.email, db)
        return invite
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Accept invite
@router.post("/invite/accept", status_code=status.HTTP_200_OK)
async def accept_project_invite(
    invite_data: AcceptInvite,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Accept a project invite using the provided token.
    
    Args:
        invite_data (AcceptInvite): The data containing the invite token.
        db (AsyncSession): The database session.
        current_user (User): The currently authenticated user.

    Returns:
        ProjectInviteRead: The updated project invite object.
    """
    
    try:
        invite = await service.accept_project_invite(invite_data.token, current_user.id, db)
        return invite
    except ValueError as e:
        # Handle different error cases with appropriate HTTP status codes
        error_message = str(e)
        if "not found" in error_message.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)
        elif "expired" in error_message.lower():
            raise HTTPException(status_code=status.HTTP_410_GONE, detail=error_message)
        elif "already" in error_message.lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=error_message)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message)