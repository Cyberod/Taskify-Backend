from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import asyncpg

# Import your routes
from app.user.routes import user_routes as user_routes
from app.auth.routes import auth_router as auth_routes
from app.user.routes import user_reset as user_reset_routes    
from app.project.routes import project_routes as project_routes
from app.task.routes import task_routes as task_routes
from app.project.routes import project_invite_routes as project_invite_routes
from app.project.routes import project_member_routes as project_member_routes
from app.project.routes import project_analytics_routes as project_analytics_routes
from app.user.routes import user_analytics_routes as user_analytics_routes

# Import settings
from app.core.config import settings

# Create FastAPI app
app = FastAPI(
    title="Taskify Backend API",
    description="A task management application backend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware

# Enhanced CORS middleware for production
allowed_origins = [
    "https://taskify-seven-iota.vercel.app",  # Your Vercel frontend
    "https://taskify-seven-iota.vercel.app/dashboard",  # Dashboard subpath
    "https://taskify-seven-iota.vercel.app/login",  # Login subpath
    "https://taskify-seven-iota.vercel.app/register",  # Register subpath
    "https://taskify-seven-iota.vercel.app/reset-password",  # Reset password
    "https://taskify-seven-iota.vercel.app/verify-email",  # Verify
    "http://localhost:3000",                   # Local development
    "http://localhost:5173",                   # Vite dev server
    "http://127.0.0.1:3000",                  # Alternative localhost
    "http://127.0.0.1:5173",                  # Alternative localhost
]


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "X-CSRF-Token",
        "X-Request-ID",
    ],
    expose_headers=["X-Request-ID"],
)



# Add a preflight handler for complex CORS requests
@app.options("/{path:path}")
async def options_handler(path: str):
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "Accept, Accept-Language, Content-Language, Content-Type, Authorization, X-Requested-With, X-CSRF-Token, X-Request-ID",
        }
    )


# Add a custom exception handler for 404 errors
@app.exception_handler(404)
async def not_found_exception_handler(request, exc):
    """
    Custom handler for 404 Not Found errors
    """
    return JSONResponse(
        status_code=404,
        content={
            "status": "error",
            "message": "Resource not found",
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url)
        }
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint for deployment platforms like Render
    """
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "taskify-backend",
            "version": "1.0.0",
            "environment": settings.ENVIRONMENT
        }
        
        # Database connectivity check using asyncpg
        try:
            # Parse the database URL to get connection parameters
            db_url = str(settings.SQLALCHEMY_DATABASE_URI)
            
            # Convert SQLAlchemy URL to asyncpg format
            # postgresql+asyncpg://user:pass@host:port/db -> postgresql://user:pass@host:port/db
            asyncpg_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
            
            # Test database connection
            conn = await asyncpg.connect(asyncpg_url)
            result = await conn.fetchval("SELECT 1")
            await conn.close()
            
            if result == 1:
                health_status["database"] = "connected"
            else:
                health_status["database"] = "disconnected"
                health_status["status"] = "degraded"
                
        except Exception as db_error:
            health_status["database"] = "disconnected"
            health_status["database_error"] = str(db_error)
            health_status["status"] = "degraded"
        
        return health_status
        
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
        )

# Simple health check without database test
@app.get("/health/simple")
async def simple_health_check():
    """
    Simple health check without database connectivity test
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "taskify-backend",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Taskify Backend API",
        "docs": "/docs",
        "health": "/health",
        "simple_health": "/health/simple",
        "project": settings.PROJECT_NAME
    }

# Include routers
app.include_router(user_routes.router)
app.include_router(auth_routes.router, prefix="/auth")
app.include_router(user_reset_routes.router)
app.include_router(project_routes.router)
app.include_router(task_routes.router)
app.include_router(project_invite_routes.router)
app.include_router(project_member_routes.router)
app.include_router(project_analytics_routes.router)
app.include_router(user_analytics_routes.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
