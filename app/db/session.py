from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from sqlalchemy.ext.declarative import declarative_base
from contextlib import asynccontextmanager

# Create async engine
engine = create_async_engine(str(settings.SQLALCHEMY_DATABASE_URI), echo=True)

# Async session factory
async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Dependency to get DB session

async def get_db():
    async with async_session() as session:
        yield session
