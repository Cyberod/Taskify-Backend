from fastapi import FASTAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi

from app.api.api import api_router
from app.core.config import settings

app = FASTAPI(
    title="Taskify API",
    description="A simple task management API",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "tasks",
            "description": "Operations with tasks",
        },
        {
            "name": "users",
            "description": "Operations with users",
        },
    ],
)

# CORS Configuration
origins = settings.BACKEND_CORS_ORIGINS
# origins = ["http://localhost:3000"]  # Allows only localhost for development

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows all origins, In production i will change to specific domains
    # allow_origins=["http://localhost:3000"],  # Allows only localhost for development
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Custom OpenAPI and documentation endpoints
@app.get("/api/openapi.json", include_in_schema=False)
async def get_open_api_endpoint():
    """Custom OpenAPI endpoint."""
    return get_openapi(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        description="Project-centric task manager API",
        routes=app.routes,
    )

@app.get("/docs", include_in_schema=False)
async def get_documentation():
    """Custom Swagger UI documentation."""
    return get_swagger_ui_html(
        openapi_url="/api/openapi.json",
        title=f"{settings.PROJECT_NAME} - Swagger UI"
    )

@app.get("/redoc", include_in_schema=False)
async def get_redoc_documentation():
    """Custom ReDoc documentation."""
    return get_redoc_html(
        openapi_url="/api/openapi.json",
        title=f"{settings.PROJECT_NAME} - ReDoc"
    )

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "app_name": settings.PROJECT_NAME,
        "description": "Project-centric task manager API",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}