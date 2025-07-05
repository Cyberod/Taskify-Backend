#!/bin/bash
set -e

echo "Starting Taskify Backend..."

# Wait for database to be ready
echo "Waiting for database..."
sleep 10

# Run database migrations
echo "Running database migrations..."
if [ -f "alembic.ini" ]; then
    echo "Found alembic.ini, running migrations..."
    alembic upgrade head
    echo "Database migrations completed."
else
    echo "No alembic.ini found, skipping migrations."
fi

# Start the application
echo "Starting FastAPI application..."
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1
