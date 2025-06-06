from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession


from app.db.session import get_db
from app.user.schemas.reset_schema import PasswordResetRequest, PasswordResetConfirm
from app.user.services.reset_service import initiate_password_reset, confirm_password_reset

router = APIRouter(prefix="/reset", tags=["Password Reset"])

@router.post("/request", status_code=status.HTTP_200_OK)
async def request_password_reset(data: PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    success = await initiate_password_reset(data.email, db)
    """ Initiate the password reset process by generating an OTP and sending it to the user's email.
            Args:
                data (PasswordResetRequest): The request body containing the email address.
                db (AsyncSession): The database session for executing queries.
            Returns:
                dict: A message indicating whether the OTP was sent successfully.
                
    """

    if not success:
        # Always return 200 to prevent email enumeration
        return {"message": "If an account with this email exists, an OTP has been sent."}

    return {"message": "If an account with this email exists, an OTP has been sent."}



@router.post("/confirm", status_code=status.HTTP_200_OK)
async def confirm_password_reset_endpoint(data: PasswordResetConfirm, db: AsyncSession = Depends(get_db)):
    """
    Confirm the password reset using the OTP and new password.
    
        Args:
            data (PasswordResetConfirm): The request body containing the email, OTP, and new password.
            db (AsyncSession): The database session for executing queries.
        
        Returns:
            dict: A message indicating whether the password was reset successfully.
            
    """
    success = await confirm_password_reset(data, db)
    
    if not success:
        return {"message": "Invalid OTP or expired. Please try again."}
    
    return {"message": "Password has been reset successfully."}

