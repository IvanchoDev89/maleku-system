#!/bin/bash
# Costa Rica Travel - Environment Check Script
# Verifies required environment variables before starting

set -e

PROJECT_DIR="/home/marcelo/Documents/costaricatravel"
ENV_FILE="$PROJECT_DIR/backend/.env"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔍 Costa Rica Travel - Environment Check"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${YELLOW}⚠️  No .env file found${NC}"
    echo "Creating .env from .env.example..."
    cp "$PROJECT_DIR/backend/.env.example" "$ENV_FILE"
    echo -e "${RED}❌ Please edit .env file and set SECRET_KEY first!${NC}"
    echo "Run: nano $ENV_FILE"
    exit 1
fi

# Load environment variables
set -a
source "$ENV_FILE"
set +a

ERRORS=0

# Check required variables
check_required() {
    local var_name=$1
    local var_value=$2

    if [ -z "$var_value" ] || [ "$var_value" = "CHANGE_ME" ] || [ "$var_value" = "your-secret-key-here" ]; then
        echo -e "${RED}❌ $var_name is not set or is using default value${NC}"
        ERRORS=$((ERRORS + 1))
    else
        echo -e "${GREEN}✓ $var_name is configured${NC}"
    fi
}

echo "Checking required environment variables..."
echo ""

# Check SECRET_KEY
if [ -z "$SECRET_KEY" ]; then
    echo -e "${RED}❌ SECRET_KEY is not set${NC}"
    ERRORS=$((ERRORS + 1))
elif [ "$SECRET_KEY" = "CHANGE_MEGenerateASecureKeyHere" ] || [ "$SECRET_KEY" = "your-secret-key-here" ]; then
    echo -e "${RED}❌ SECRET_KEY is using default value - MUST be changed!${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✓ SECRET_KEY is configured${NC}"
fi

# Check DEBUG
if [ "$DEBUG" = "true" ]; then
    echo -e "${YELLOW}⚠️  DEBUG is enabled - not recommended for production${NC}"
else
    echo -e "${GREEN}✓ DEBUG is disabled (production safe)${NC}"
fi

# Check ENVIRONMENT
if [ "$ENVIRONMENT" = "production" ]; then
    if [ "$DEBUG" = "true" ]; then
        echo -e "${RED}❌ Cannot run in production with DEBUG=true${NC}"
        ERRORS=$((ERRORS + 1))
    fi
    echo -e "${GREEN}✓ Running in production mode${NC}"
else
    echo -e "${YELLOW}⚠️  Running in $ENVIRONMENT mode${NC}"
fi

echo ""
echo "=========================================="

if [ $ERRORS -gt 0 ]; then
    echo -e "${RED}❌ Found $ERRORS error(s) - please fix before running${NC}"
    echo ""
    echo "To fix:"
    echo "  1. Edit .env file: nano $ENV_FILE"
    echo "  2. Generate a new SECRET_KEY:"
    echo "     python3 -c \"import secrets; print(secrets.token_hex(32))\""
    echo "  3. Set DEBUG=false for production"
    exit 1
else
    echo -e "${GREEN}✅ All checks passed!${NC}"
    echo ""
    echo "You can now start the servers:"
    echo "  ./start-dev.sh"
    exit 0
fi
