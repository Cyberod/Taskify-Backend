from fastapi import FastAPI
from app.user.routes import user as user_routes

app = FastAPI()
app.include_router(user_routes.router)
