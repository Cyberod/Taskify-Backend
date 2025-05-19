from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.user.schemas.user import UserLogin
from app.auth.services.auth_service import authenticate_user
from app.db.session import get_db
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(tags=["Auth"])

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    Authenticate user and return access token.
    """
    user_data = UserLogin(email=form_data.username, password=form_data.password)
    token = await authenticate_user(user_data, db)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {"access_token": token, "token_type": "bearer"}