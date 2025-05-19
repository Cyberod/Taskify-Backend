from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext
from fastapi import HTTPException, status

from app.user.models.user_models import User
from app.user.schemas.user_schema import UserLogin
from app.auth.utils.jwt_handler import create_access_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def authenticate_user(user_data: UserLogin, db: AsyncSession) -> str:
    query = select(User).where(User.email == user_data.email)
    result = await db.execute(query)
    user = result.scalars().first()

    if not user or not pwd_context.verify(user_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    return create_access_token(subject=user.id)
