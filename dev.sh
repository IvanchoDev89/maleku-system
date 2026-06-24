#!/bin/bash
# Development startup script — arranca backend y frontend
set -e

BACKEND_DIR="$(cd "$(dirname "$0")" && pwd)/backend"
FRONTEND_DIR="$(cd "$(dirname "$0")" && pwd)/frontend"

echo "=== Arrancando Backend (uvicorn) ==="
cd "$BACKEND_DIR"
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "=== Arrancando Frontend (Nuxt) ==="
cd "$FRONTEND_DIR"
npx nuxt dev &
FRONTEND_PID=$!

echo ""
echo "Backend PID: $BACKEND_PID  →  http://localhost:8000"
echo "Frontend PID: $FRONTEND_PID →  http://localhost:3000"
echo ""
echo "Presiona Ctrl+C para detener ambos."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
