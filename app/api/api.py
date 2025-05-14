from fastapi import APIRouter
from app.api.endpoints import auth, users

api_router = APIRouter()

# Include routers from endpoints
api_router.include_router(auth.router, tags=["authentication"], prefix="/auth")
api_router.include_router(users.router, tags=["users"], prefix="/users")

# Additional routers will be added here as we develop more features
# Examples:
# api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
# api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])