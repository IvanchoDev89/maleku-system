#!/bin/bash
# Backup script for PostgreSQL database
# Usage: ./backup-db.sh [output-dir]
# Requires: POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, POSTGRES_HOST, POSTGRES_PORT
# or DATABASE_URL env vars

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Source environment
if [ -f "$PROJECT_DIR/backend/.env" ]; then
    set -a
    source "$PROJECT_DIR/backend/.env"
    set +a
fi

OUTPUT_DIR="${1:-$PROJECT_DIR/backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-7}"

mkdir -p "$OUTPUT_DIR"

# Parse DATABASE_URL if set, otherwise use individual vars
if [ -n "${DATABASE_URL:-}" ]; then
    PG_USER=$(echo "$DATABASE_URL" | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
    PG_PASSWORD=$(echo "$DATABASE_URL" | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p')
    PG_HOST=$(echo "$DATABASE_URL" | sed -n 's/.*@\([^:]*\):.*/\1/p')
    PG_PORT=$(echo "$DATABASE_URL" | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
    PG_DB=$(echo "$DATABASE_URL" | sed -n 's/.*\/\([^?]*\).*/\1/p')
else
    PG_USER="${POSTGRES_USER:-postgres}"
    PG_PASSWORD="${POSTGRES_PASSWORD:-postgres}"
    PG_HOST="${POSTGRES_HOST:-localhost}"
    PG_PORT="${POSTGRES_PORT:-5434}"
    PG_DB="${POSTGRES_DB:-costaricatravel}"
fi

BACKUP_FILE="$OUTPUT_DIR/${PG_DB}_${TIMESTAMP}.sql.gz"
LATEST_LINK="$OUTPUT_DIR/${PG_DB}_latest.sql.gz"

echo "=== Backup started: $(date) ==="
echo "Database: $PG_DB on $PG_HOST:$PG_PORT"
echo "Output: $BACKUP_FILE"

export PGPASSWORD="$PG_PASSWORD"

pg_dump \
    --host="$PG_HOST" \
    --port="$PG_PORT" \
    --username="$PG_USER" \
    --dbname="$PG_DB" \
    --no-owner \
    --no-acl \
    --compress=9 \
    --verbose \
    | gzip > "$BACKUP_FILE"

unset PGPASSWORD

# Create/update symlink to latest backup
ln -sf "$BACKUP_FILE" "$LATEST_LINK"

BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
echo "Backup size: $BACKUP_SIZE"

# Remove backups older than retention period
find "$OUTPUT_DIR" -name "${PG_DB}_*.sql.gz" -mtime "+$RETENTION_DAYS" -delete 2>/dev/null || true

echo "=== Backup completed: $(date) ==="
echo "Cleaned up backups older than $RETENTION_DAYS days"
