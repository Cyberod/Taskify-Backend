

from app.core.config import settings
from sqlalchemy.future import select
from app.user.models.user_models import User
import logging
from fastapi_mail import FastMail, MessageSchema, MessageType

# Set up logging
logger = logging.getLogger(__name__)

async def get_user_by_email(email: str, db) -> 'User | None':
    """
    Retrieve a user by their email address.

        Args:
            email (str): The email address of the user.
            db: The database session for executing queries.

        Returns:
            User | None: The user object if found, otherwise None.
    """
    query = select(User).where(User.email == email)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def send_reset_email(email_to: str, otp: str) -> bool:
    """
    Send a password reset email with an OTP code to the user using FastMail.

        Args:
            email_to (str): The recipient's email address.
            otp (str): The OTP code to be sent.

        Returns:
            bool: True if the email was sent successfully, False otherwise.
    """
    message = MessageSchema(
        subject=f"{settings.PROJECT_NAME} - Password Reset Request",
        recipients=[email_to],
        body=f"""
        <p>Dear User,</p>
        <p>You have requested a password reset. Please use the following OTP to reset your password:</p>
        <h2>{otp}</h2>
        <p>This OTP is valid for 15 minutes.</p>
        <p>If you did not request this, please ignore this email.</p>
        <p>Best regards,<br>The {settings.PROJECT_NAME} Team</p>
        """,
        subtype=MessageType.html
    )
    fm = FastMail(settings.fastmail_config)
    try:
        await fm.send_message(message)
        return True
    except Exception as e:
        print(f"Failed to send email to {email_to}: {e}")
        return False
    


async def send_invite_email(email_to: str, token: str) -> bool:
    """
    Send a project invitation email with a token to the user using FastMail.

        Args:
            email_to (str): The recipient's email address.
            token (str): The invite token to be sent.

        Returns:
            bool: True if the email was sent successfully, False otherwise.
        """
    # Remember to replace with your actual frontend URL
    invite_link = f"{settings.FRONTEND_URL}/accept-invite?token={token}"
    message = MessageSchema(
        subject=f"{settings.PROJECT_NAME} - Project Invitation",
        recipients=[email_to],
        body=f"""
        <p>Hello,</p>
        <p>You have been invited to join a project on {settings.PROJECT_NAME}.</p>
        <p>Click the link below to accept the invitation:</p>
        <p><a href="{invite_link}">Accept Project Invitation</a></p>
        <p>This invitation expires in 48 hours.</p>
        <p>Best regards,<br>The {settings.PROJECT_NAME} Team</p>
        """,
        subtype=MessageType.html
    )

    fm = FastMail(settings.fastmail_config)
    try:
        await fm.send_message(message)
        return True
    except Exception as e:
        logger.error(f"Failed to send invite email to {email_to}: {e}")
        return False
