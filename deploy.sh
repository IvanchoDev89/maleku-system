#!/bin/bash

# Costa Rica Travel - Deployment Script
# Usage: ./deploy.sh [backend|frontend|all]

set -e

echo "🚀 Costa Rica Travel Deployment Script"
echo "========================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

deploy_backend() {
    log_info "Deploying Backend to Railway..."
    
    cd backend
    
    # Check if railway CLI is installed
    if ! command -v railway &> /dev/null; then
        log_warn "Railway CLI not found. Installing..."
        npm install -g @railway/cli
    fi
    
    # Check if logged in
    if ! railway whoami &> /dev/null; then
        log_error "Not logged in to Railway. Run: railway login"
        exit 1
    fi
    
    # Link to project if not already linked
    if [ ! -f .railway.json ]; then
        log_info "Linking to Railway project..."
        railway link
    fi
    
    # Deploy
    log_info "Pushing to Railway..."
    railway up --detach
    
    # Run migrations
    log_info "Running database migrations..."
    railway run alembic upgrade head
    
    log_info "Backend deployed successfully!"
    cd ..
}

deploy_frontend() {
    log_info "Deploying Frontend to Vercel..."
    
    cd frontend
    
    # Check if vercel CLI is installed
    if ! command -v vercel &> /dev/null; then
        log_warn "Vercel CLI not found. Installing..."
        npm install -g vercel
    fi
    
    # Check if logged in
    if ! vercel whoami &> /dev/null; then
        log_error "Not logged in to Vercel. Run: vercel login"
        exit 1
    fi
    
    # Deploy
    log_info "Building and deploying to Vercel..."
    vercel --prod
    
    log_info "Frontend deployed successfully!"
    cd ..
}

# Main
if [ $# -eq 0 ]; then
    echo "Usage: ./deploy.sh [backend|frontend|all]"
    echo ""
    echo "Options:"
    echo "  backend  - Deploy only backend to Railway"
    echo "  frontend - Deploy only frontend to Vercel"
    echo "  all      - Deploy both backend and frontend"
    exit 1
fi

case "$1" in
    backend)
        deploy_backend
        ;;
    frontend)
        deploy_frontend
        ;;
    all)
        deploy_backend
        deploy_frontend
        log_info "Full deployment complete!"
        ;;
    *)
        log_error "Unknown option: $1"
        echo "Usage: ./deploy.sh [backend|frontend|all]"
        exit 1
        ;;
esac
