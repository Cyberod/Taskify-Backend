from fastapi import FASTAPI
from fastapi.middleware.cors import CORSMiddleware


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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, In production i will change to specific domains
    # allow_origins=["http://localhost:3000"],  # Allows only localhost for development
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to Taskify API!"}