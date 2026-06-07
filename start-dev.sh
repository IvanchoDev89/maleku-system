#!/bin/bash
# Costa Rica Travel - Development Server Starter
# Usage: ./start-dev.sh

PROJECT_DIR="/home/marcelo/Documents/costaricatravel.dev"
BACKEND_PORT=8000
FRONTEND_PORT=3000

echo "🚀 Starting Costa Rica Travel..."
echo "================================"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    pkill -f "uvicorn app.main:app" 2>/dev/null
    pkill -f "npm" 2>/dev/null
    pkill -f "nuxt" 2>/dev/null
    pkill -f "node .output" 2>/dev/null
    echo "✅ Servers stopped"
    exit 0
}

# Trap Ctrl+C and exit
trap cleanup SIGINT SIGTERM EXIT

# Start Backend
echo "📡 Starting Backend on port $BACKEND_PORT..."
cd "$PROJECT_DIR/backend"
export PYTHONPATH="$PROJECT_DIR/backend"

# Load environment variables
if [ -f ".env" ]; then
    set -a
    source .env
    set +a
fi

# Start backend in background
python3 -m uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT &
BACKEND_PID=$!
sleep 3

# Start Frontend (Development mode with hot-reload)
echo "🖥️ Starting Frontend on port $FRONTEND_PORT..."
cd "$PROJECT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!

# Verify servers
echo ""
echo "================================"
echo "✅ Servers started successfully!"
echo ""
echo "   🌐 Frontend: http://localhost:$FRONTEND_PORT"
echo "   🔌 Backend:  http://localhost:$BACKEND_PORT"
echo "   📚 API:      http://localhost:$BACKEND_PORT/api/v1"
echo ""
echo "   🧪 Health:   http://localhost:$BACKEND_PORT/health"
echo "   📖 Docs:    http://localhost:$BACKEND_PORT/docs"
echo ""
echo "Press Ctrl+C to stop all servers"
echo "================================"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID