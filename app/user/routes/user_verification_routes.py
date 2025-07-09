from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.user.schemas.user_verification_schema import (
    EmailVerificationRequest,
    EmailVerificationConfirm,
    ResendVerificationRequest
)
from app.user.services.user_verification_service import (
    send_verification_code,
    resend_verification_code,
    verify_email
)


router = APIRouter(prefix="/verify", tags=["Email Verification"])

@router.post("/send", status_code=status.HTTP_200_OK)
async def send_verification_email_endpoint(
    data: EmailVerificationRequest, 
    db: AsyncSession = Depends(get_db)
):
    """
    Send verification email to user.
    
    Args:
        data (EmailVerificationRequest): The request body containing the email address.
        db (AsyncSession): The database session for executing queries.
        
    Returns:
        dict: A message indicating whether the verification email was sent.
    """
    try:
        success = await send_verification_code(data.email, db)
        if not success:
            # Don't reveal if email exists or not for security
            return {"message": "If an account with this email exists, a verification code has been sent."}
        
        return {"message": "Verification code sent to your email address."}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email"
        )

@router.post("/resend", status_code=status.HTTP_200_OK)
async def resend_verification_email_endpoint(
    data: ResendVerificationRequest, 
    db: AsyncSession = Depends(get_db)
):
    """
    Resend verification email to user with rate limiting.
    
    Args:
        data (ResendVerificationRequest): The request body containing the email address.
        db (AsyncSession): The database session for executing queries.
        
    Returns:
        dict: A message indicating whether the verification email was resent.
    """
    try:
        success = await resend_verification_code(data.email, db)
        if not success:
            return {"message": "If an account with this email exists, a verification code has been sent."}
        
        return {"message": "Verification code resent to your email address."}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resend verification email"
        )

@router.post("/confirm", status_code=status.HTTP_200_OK)
async def verify_email_endpoint(
    data: EmailVerificationConfirm, 
    db: AsyncSession = Depends(get_db)
):
    """
    Verify email using OTP and activate user account.
    
    Args:
        data (EmailVerificationConfirm): The request body containing email and OTP.
        db (AsyncSession): The database session for executing queries.
        
    Returns:
        dict: A message indicating whether the email was verified successfully.
    """
    try:
        success = await verify_email(data, db)
        
        if success:
            return {
                "message": "Email verified successfully! Your account is now active.",
                "verified": True
            }
        else:
            return {
                "message": "Verification failed. Please try again.",
                "verified": False
            }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during verification"
        )