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
while ! wget -qO- http://backend:8000/health >/dev/null 2>&1; do
    echo "Backend not ready yet, waiting..."
    sleep 2
done
echo "Backend is ready!"

# Ensure all required modules are installed
if [ ! -d "/app/node_modules/@nuxt/image" ]; then
    echo "Installing @nuxt/image..."
    npm install @nuxt/image
fi

# Start development server
echo "Starting Nuxt development server..."
exec npm run dev
