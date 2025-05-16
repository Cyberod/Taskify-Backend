from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.user.schemas.user import UserLogin
from app.auth.services.auth_service import authenticate_user
from app.db.session import get_db

router = APIRouter(tags=["Auth"])

@router.post("/login")
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Authenticate user and return access token.
    """
    token = await authenticate_user(user_data, db)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {"access_token": token, "token_type": "bearer"}