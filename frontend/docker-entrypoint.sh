#!/bin/sh
set -e

echo "=== FRONTEND ENTRYPOINT ==="

# Always ensure dependencies are installed (handles fresh anonymous volumes)
if [ ! -d "/app/node_modules/@nuxt/image" ] || [ ! -d "/app/node_modules/nuxt" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Wait for backend to be ready
echo "Waiting for backend..."
while ! wget -qO- http://backend:8000/health >/dev/null 2>&1; do
    echo "Backend not ready yet, waiting..."
    sleep 2
done
echo "Backend is ready!"

# Start development server
echo "Starting Nuxt development server..."
exec npm run dev
