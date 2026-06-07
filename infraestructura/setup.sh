#!/bin/bash
set -e

echo "=========================================="
echo "Costa Rica Travel - Setup Script"
echo "=========================================="

# Colours for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}Warning: Running as root is not recommended!${NC}"
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${YELLOW}Created .env from template. Please edit it with secure values!${NC}"
        echo ""
        echo "Edit these values in .env:"
        echo "  - DB_PASSWORD"
        echo "  - REDIS_PASSWORD"
        echo "  - SECRET_KEY"
        echo "  - STRIPE_SECRET_KEY"
    else
        echo -e "${RED}No .env.example found!${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}.env file exists${NC}"
fi

# Verify required ports are available
check_port() {
    local port=$1
    local name=$2
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${RED}Port $port ($name) is already in use!${NC}"
        return 1
    fi
    return 0
}

echo ""
echo "Checking ports..."
check_port 5432 "PostgreSQL" || echo "PostgreSQL conflict"
check_port 6379 "Redis" || echo "Redis conflict"
check_port 8000 "API" || echo "API conflict"
check_port 3000 "Web" || echo "Frontend conflict"
check_port 80 "Nginx" || echo "Nginx conflict"

echo ""
echo -e "${GREEN}All checks passed!${NC}"
echo ""
echo "To start the application:"
echo "  1. Edit .env with secure values"
echo "  2. Run: docker-compose up -d"
echo "  3. Check health: curl http://localhost:8000/health"
echo ""
echo "To check logs:"
echo "  docker-compose logs -f api"
echo ""
echo "=========================================="