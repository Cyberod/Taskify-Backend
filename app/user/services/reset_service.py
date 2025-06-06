from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta


from app.user.models.reset_models import PasswordResetCode
from app.auth.utils.otp import generate_otp
from app.auth.utils.email_sender import send_reset_email, get_user_by_email
from app.core.config import settings
from app.user.schemas.reset_schema import PasswordResetConfirm
from app.user.models.reset_models import PasswordResetCode
from app.auth.utils.hashing import Hasher
from sqlalchemy import select



async def initiate_password_reset(email: str, db: AsyncSession) -> bool:
    """
    Initiate the password reset process by generating an OTP and sending it to the user's email.
    
        Args:
            email (str): The email address of the user requesting a password reset.
            db (AsyncSession): The database session for executing queries.
            
        Returns:
            bool: True if the OTP was sent successfully, False if user was not found.
    """
    
    # Retrieve the user by email
    user =  await get_user_by_email(email, db)

    if not user:
        # User not found but we return False to avoid revealing user existence
        return False
        
    # Generate a new OTP
    otp =  generate_otp()
    print(f"Generated OTP for user {user.email}: {otp}")

    expires_at = datetime.utcnow() + timedelta(minutes=15) # OTP valid for 15 minutes

    # Create a new Password reset code
    reset_code = PasswordResetCode(
        user_id=user.id,
        code=otp,
        expires_at=expires_at,
        is_used=False
    )

    # Save to database
    db.add(reset_code)
    await db.commit()

    # Send the OTP to the user's email
    return await send_reset_email(email, otp)
    

async def confirm_password_reset(data:PasswordResetConfirm, db: AsyncSession) -> bool:
    """
    Confirm the password reset by verifying the OTP and updating the user's password.
    
        Args:
            data (PasswordResetConfirm): The data containing email, OTP, and new password.
            db (AsyncSession): The database session for executing queries.
            
        Returns:
            bool: True if the password was reset successfully, False otherwise.
    """

    # Find User
    user =  await get_user_by_email(data.email, db)
    if not user:
        return False
    
    # Find valid OTP
    stmt = select(PasswordResetCode).where(
        PasswordResetCode.user_id == user.id,
        PasswordResetCode.code == data.otp,
        PasswordResetCode.is_used == False,
        PasswordResetCode.expires_at > datetime.utcnow()
    )

    result = await db.execute(stmt)
    reset_code = result.scalar_one_or_none()
    if not reset_code:
        print(f"Invalid or expired OTP for user {data.email}.")
        return False
    
    # Update user's password
    user.password = Hasher.get_password_hash(data.new_password)
    reset_code.is_used = True  # The OTP will be marked as used
    reset_code.expires_at = datetime.utcnow()  # The expiration of the OTP will be set to now
    await db.commit()
    print(f"Password reset successful for user {data.email}.")
    return True