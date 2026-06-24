#!/bin/bash
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
INFRA_DIR="$SCRIPT_DIR"

print_header() {
    echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  Costa Rica Travel - Startup${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
    echo ""
}

print_status() {
    echo -e "${GREEN}[+]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[X]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[i]${NC} $1"
}

# Check if .env exists
check_env() {
    if [ ! -f "$INFRA_DIR/.env" ]; then
        if [ -f "$INFRA_DIR/.env.example" ]; then
            print_warning(".env not found, creating from template..."
            cp "$INFRA_DIR/.env.example" "$INFRA_DIR/.env"
            print_status("Created .env - please edit with secure values!")
            echo ""
            echo "Edit these values in .env before continuing:"
            echo "  - DB_PASSWORD ( PostgreSQL password)"
            echo "  - REDIS_PASSWORD"
            echo "  - SECRET_KEY (generate a secure key)"
            echo ""
            read -p "Press Enter to edit .env file..."
            ${EDITOR:-nano} "$INFRA_DIR/.env"
        else
            print_error(".env.example not found"
            exit 1
        fi
    fi
}

# Check Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi

    if ! command -v docker &> /dev/null || ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi

    print_status "Docker: $(docker --version | cut -d' ' -f3 | cut -d',' -f1)"
    print_status "Docker Compose: $(docker compose version --short)"
}

# Check ports
check_ports() {
    print_status "Checking required ports..."

    PORTS_OK=true

    for port in 5432 6379; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            print_warning "Port $port is in use (may conflict)"
            PORTS_OK=false
        fi
    done

    if [ "$PORTS_OK" = true ]; then
        print_status "All required ports available"
    fi
}

# Start database services
start_databases() {
    print_status "Starting database services..."

    cd "$INFRA_DIR"

    # Start only db and redis
    docker compose up -d db redis

    # Wait for PostgreSQL
    print_status "Waiting for PostgreSQL..."
    for i in {1..30}; do
        if docker compose exec -T db pg_isready -U crtravel &>/dev/null; then
            print_status "PostgreSQL is ready"
            break
        fi
        sleep 1
    done

    # Wait for Redis
    print_status "Waiting for Redis..."
    for i in {1..10}; do
        if docker compose exec -T redis redis-cli ping &>/dev/null; then
            print_status "Redis is ready"
            break
        fi
        sleep 1
    done

    print_status "Databases started"
}

# Run migrations
run_migrations() {
    print_status "Running database migrations..."

    cd "$BACKEND_DIR"

    # Apply migrations using SQLAlchemy create_all
    python3 -c "
import asyncio
from app.core.database import engine, Base
from app.models import *
from app.core.config import settings

async def migrate():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print('Migrations applied successfully')

asyncio.run(migrate())
"

    print_status "Migrations completed"
}

# Initialize database with seed data
init_database() {
    print_status "Initializing database with seed data..."

    cd "$BACKEND_DIR"
    python3 init_db.py

    print_status "Database initialized"
}

# Start API
start_api() {
    print_status "Starting API server..."

    cd "$BACKEND_DIR"

    # Run in background
    nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/api.log 2>&1 &
    API_PID=$!

    echo $API_PID > /tmp/api.pid

    # Wait for API to be ready
    for i in {1..20}; do
        if curl -s http://localhost:8000/health &>/dev/null; then
            print_status "API is running on http://localhost:8000"
            print_info "API docs: http://localhost:8000/docs"
            return 0
        fi
        sleep 1
    done

    print_error "API failed to start"
    cat /tmp/api.log
    return 1
}

# Build frontend
build_frontend() {
    print_status "Building frontend..."

    cd "$FRONTEND_DIR"

    # Install deps if needed
    if [ ! -d "node_modules" ]; then
        print_status "Installing frontend dependencies..."
        npm ci --silent
    fi

    # Build
    npm run build

    print_status "Frontend built successfully"
}

# Test API with curl
test_api() {
    print_status "Testing API endpoints..."

    BASE_URL="http://localhost:8000/api/v1"

    # Test health
    HEALTH=$(curl -s http://localhost:8000/health)
    if echo "$HEALTH" | grep -q "healthy"; then
        print_status "✓ Health check"
    else
        print_error "✗ Health check failed"
    fi

    # Test public destinations
    DESTINATIONS=$(curl -s "$BASE_URL/destinations")
    if echo "$DESTINATIONS" | grep -q "Guanacaste"; then
        print_status "✓ Destinations endpoint"
    else
        print_warning "! Destinations may need data"
    fi

    # Test blog posts
    POSTS=$(curl -s "$BASE_URL/blog")
    if echo "$POSTS" | grep -q "content"; then
        print_status "✓ Blog endpoint"
    else
        print_warning "! Blog may need data"
    fi

    print_status "API tests completed"
}

# Print help
print_help() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start       - Start all services (default)"
    echo "  db         - Start only databases"
    echo "  api        - Start only API"
    echo "  test       - Test API endpoints"
    echo "  build      - Build frontend"
    echo "  status     - Check status"
    echo "  stop       - Stop all services"
    echo "  logs       - Show logs"
    echo "  clean      - Clean up containers and volumes"
    echo ""
}

# Show status
show_status() {
    echo ""
    echo "═══════════════════════════════════════════"
    echo "  Services Status"
    echo "════��══════════════════════════════════════"
    echo ""

    # Check Docker
    echo "Docker Services:"
    cd "$INFRA_DIR"
    docker compose ps 2>/dev/null || echo "  (not running)"
    echo ""

    # Check API
    if curl -s http://localhost:8000/health &>/dev/null; then
        echo -e "${GREEN}API: Running${NC} (http://localhost:8000)"
    else
        echo -e "${RED}API: Not running${NC}"
    fi
    echo ""
}

# Stop services
stop_services() {
    print_status "Stopping services..."

    # Stop API
    if [ -f /tmp/api.pid ]; then
        kill $(cat /tmp/api.pid) 2>/dev/null || true
        rm /tmp/api.pid
    fi

    # Stop Docker
    cd "$INFRA_DIR"
    docker compose stop 2>/dev/null || true

    print_status "Services stopped"
}

# Show logs
show_logs() {
    cd "$INFRA_DIR"

    if [ "$1" = "api" ]; then
        tail -f /tmp/api.log 2>/dev/null || echo "No API logs found"
    else
        docker compose logs -f "${@:-}"
    fi
}

# Clean up
clean_up() {
    print_warning "This will remove all containers and volumes!"
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd "$INFRA_DIR"
        docker compose down -v
        print_status "Cleaned up"
    fi
}

# Main
main() {
    print_header

    case "${1:-start}" in
        start)
            check_docker
            check_env
            check_ports
            start_databases
            run_migrations
            init_database
            start_api
            test_api
            show_status
            ;;
        db)
            check_docker
            start_databases
            ;;
        api)
            start_api
            ;;
        test)
            test_api
            ;;
        build)
            build_frontend
            ;;
        status)
            show_status
            ;;
        stop)
            stop_services
            ;;
        logs)
            show_logs "${@:2}"
            ;;
        clean)
            clean_up
            ;;
        *)
            print_help
            ;;
    esac
}

main "$@"
