from fastapi import FastAPI
from app.user.routes import user as user_routes
from app.auth.routes import auth_router as auth_routes

app = FastAPI()

app.include_router(user_routes.router)
app.include_router(auth_routes.router)


