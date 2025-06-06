from fastapi import FastAPI
from app.user.routes import user_routes as user_routes
from app.auth.routes import auth_router as auth_routes
from app.user.routes import user_reset as user_reset_routes


app = FastAPI()

app.include_router(user_routes.router)
app.include_router(auth_routes.router, prefix="/auth")
app.include_router(user_reset_routes.router)


