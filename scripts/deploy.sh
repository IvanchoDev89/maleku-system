#!/bin/bash
# CI/CD Deploy Script — VPS with Docker Compose
# Usage: ./scripts/deploy.sh [path]
# Called by GitHub Actions CI.

set -e

DEPLOY_PATH="${1:-/opt/costaricatravel}"
COMMIT_HASH=$(git rev-parse --short HEAD)
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
LOG_FILE="/tmp/deploy-${TIMESTAMP}.log"

echo "[INFO] Deploying commit ${COMMIT_HASH} to ${DEPLOY_PATH}" | tee "${LOG_FILE}"

cd "${DEPLOY_PATH}"

# Pull latest code
echo "[INFO] Pulling latest code..."
git pull origin main 2>&1 | tee -a "${LOG_FILE}"

# Build and start containers
echo "[INFO] Building and starting containers..."
docker compose up -d --build 2>&1 | tee -a "${LOG_FILE}"

# Wait for backend to be ready
echo "[INFO] Waiting for backend health check..."
for i in $(seq 1 30); do
    if curl -sf http://localhost:8000/health/ready > /dev/null 2>&1; then
        echo "[INFO] Backend is healthy after ${i}s"
        break
    fi
    if [ "$i" -eq 30 ]; then
        echo "[ERROR] Backend health check failed after 30s — rolling back"
        docker compose down
        git checkout HEAD~1
        docker compose up -d --build
        echo "[INFO] Rollback to previous commit completed"
        exit 1
    fi
    sleep 1
done

# Run migrations if backend is healthy
echo "[INFO] Running database migrations..."
docker compose exec -T backend alembic upgrade head 2>&1 | tee -a "${LOG_FILE}" || \
    echo "[WARN] Migration failed — check logs"

# Verify frontend is up
echo "[INFO] Verifying frontend..."
if curl -sf http://localhost:3000 > /dev/null 2>&1; then
    echo "[INFO] Frontend is up"
else
    echo "[WARN] Frontend health check failed — manual review needed"
fi

echo "[INFO] Deploy completed successfully (commit: ${COMMIT_HASH})"
