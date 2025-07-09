from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, status


from app.user.models.email_verification_models import EmailVerification
from app.user.models.user_models import User
from app.auth.utils.otp import generate_otp
from app.auth.utils.hashing import Hasher
from app.auth.utils.email_sender import send_verification_email, get_user_by_email
from app.user.schemas.user_verification_schema import EmailVerificationConfirm


# Constants
OTP_EXPIRY_MINUTES = 10
MAX_RESEND_ATTEMPTS = 3
RESEND_COOLDOWN_SECONDS = 30
MAX_VERIFICATION_ATTEMPTS = 5

async def create_verification_code(user_id: str, db: AsyncSession) -> str:
    """
    Create a new email verification code for the user.
    Args:
        user_id (str): The ID of the user.
        db (AsyncSession): The database session.

        Returns:
        str: The generated verification code.
    """
    stmt = select(EmailVerification).where(and_(
        EmailVerification.user_id == user_id,
        EmailVerification.is_used == False,
        EmailVerification.expires_at > datetime.now(timezone.utc)
    ))

    result = await db.execute(stmt)
    existing_codes = result.scalars().all()

    for code in existing_codes:
        code.is_used = True

    # Generate new OTP
    otp = generate_otp()
    hashed_otp = Hasher.get_password_hash(otp)

    # Create new verification record
    verification = EmailVerification(
        user_id=user_id,
        code=hashed_otp,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRY_MINUTES),
        resend_count=0,
    )

    db.add(verification)
    await db.commit()

    return otp


async def send_verification_code(email: str, db: AsyncSession) -> bool:
    """    Send a verification code to the user's email.
    Args:
        email (str): The user's email address.
        db (AsyncSession): The database session.
        
        Returns:
        bool: True if the email was sent successfully, False otherwise.
    """

    user = await get_user_by_email(email, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account already verified"
        )
    
    # Generate and send OTP
    otp = await create_verification_code(user.id, db)
    print(f"Verification code sent to {email}: {otp}") # For debugging purposes
    return await send_verification_email(email, otp)
      




async def resend_verification_code(email: str, db: AsyncSession) -> bool:
    """
    Resend the verification code to the user's email.
    Args:
        email (str): The user's email address.
        db (AsyncSession): The database session.

        Returns:
        bool: True if the email was sent successfully, False otherwise.
    """
    user = await get_user_by_email(email, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account already verified"
        )

    # Check recent verification record
    stmt = select(EmailVerification).where(
        and_(
            EmailVerification.user_id == user.id,
            EmailVerification.expires_at > datetime.now(timezone.utc)
        )
    ).order_by(EmailVerification.created_at.desc())
    
    result = await db.execute(stmt)
    recent_verification = result.scalar_one_or_none()
    
    if recent_verification:
        # Check resend limits
        if recent_verification.resend_count >= MAX_RESEND_ATTEMPTS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Maximum resend attempts reached. Please try again later."
            )
        
        # Check cooldown period
        if recent_verification.last_resend_at:
            time_since_last_resend = datetime.now(timezone.utc) - recent_verification.last_resend_at
            if time_since_last_resend.total_seconds() < RESEND_COOLDOWN_SECONDS:
                remaining_time = RESEND_COOLDOWN_SECONDS - int(time_since_last_resend.total_seconds())
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Please wait {remaining_time} seconds before requesting another code."
                )
        
        # Update resend count and timestamp
        recent_verification.resend_count += 1
        recent_verification.last_resend_at = datetime.now(timezone.utc)
        await db.commit()
    
    # Generate and send new OTP
    otp = await create_verification_code(user.id, db)
    print(f"Resending verification code to {email}: {otp}")  # For debugging purposes
    return await send_verification_email(email, otp)


async def verify_email(data: EmailVerificationConfirm, db: AsyncSession) -> bool:
    """
    Verify email using OTP and activate user account.
    """
    user = await get_user_by_email(data.email, db)
    if not user:
        return False
    
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is already verified"
        )
    
    # Find valid verification code
    stmt = select(EmailVerification).where(
        and_(
            EmailVerification.user_id == user.id,
            EmailVerification.is_used == False,
            EmailVerification.expires_at > datetime.now(timezone.utc)
        )
    ).order_by(EmailVerification.created_at.desc())
    
    result = await db.execute(stmt)
    verification = result.scalar_one_or_none()
    
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code"
        )
    
    # Check attempt limits
    if verification.attempts >= MAX_VERIFICATION_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Maximum verification attempts reached. Please request a new code."
        )
    
    # Verify OTP
    verification.attempts += 1
    
    if not Hasher.verify_password(data.otp, verification.code):
        await db.commit()  # Save the attempt count
        remaining_attempts = MAX_VERIFICATION_ATTEMPTS - verification.attempts
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid verification code. {remaining_attempts} attempts remaining."
        )
    
    # Success - activate user and mark verification as used
    user.is_verified = True
    user.is_active = True
    verification.is_used = True
    
    await db.commit()
    return True
