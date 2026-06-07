#!/bin/bash
set -e

echo "=== BACKEND ENTRYPOINT ==="

# Wait for PostgreSQL
echo "Waiting for PostgreSQL..."
while ! nc -z postgres 5432; do
  sleep 1
done
echo "PostgreSQL is ready!"

# Wait for Redis
echo "Waiting for Redis..."
while ! nc -z redis 6379; do
  sleep 1
done
echo "Redis is ready!"

# Activate virtual environment
source /app/venv/bin/activate

# Run migrations
echo "Running database migrations..."
cd /app
python -m alembic upgrade head || echo "No migrations to run or alembic not configured"

# Start the application with hot reload
echo "Starting FastAPI with hot reload..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir /app
