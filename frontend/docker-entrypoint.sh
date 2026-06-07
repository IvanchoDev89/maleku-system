#!/bin/sh
set -e

echo "=== FRONTEND ENTRYPOINT ==="

# Install dependencies if node_modules is missing or empty
if [ ! -d "/app/node_modules" ] || [ -z "$(ls -A /app/node_modules 2>/dev/null)" ]; then
    echo "Installing dependencies..."
    npm install
    npm install lucide-vue-next
fi

# Wait for backend to be ready
echo "Waiting for backend..."
while ! wget --no-verbose --tries=1 --spider http://backend:8000/health 2>/dev/null; do
    echo "Backend not ready yet, waiting..."
    sleep 2
done
echo "Backend is ready!"

# Start development server
echo "Starting Nuxt development server..."
exec npm run dev
