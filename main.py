from fastapi import FastAPI
from app.user.routes import user_routes as user_routes
from app.auth.routes import auth_router as auth_routes
from app.user.routes import user_reset as user_reset_routes
from app.project.routes import project_routes as project_routes
from app.task.routes import task_routes as task_routes
from app.project.routes import project_invite_routes as project_invite_routes
from app.project.routes import project_member_routes as project_member_routes
from app.project.routes import project_analytics_routes as project_analytics_routes
from app.user.routes import user_analytics_routes as user_analytics_routes

app = FastAPI()

app.include_router(user_routes.router)
app.include_router(auth_routes.router, prefix="/auth")
app.include_router(user_reset_routes.router)
app.include_router(project_routes.router)
app.include_router(task_routes.router)
app.include_router(project_invite_routes.router)
app.include_router(project_member_routes.router)
app.include_router(project_analytics_routes.router)
app.include_router(user_analytics_routes.router)

