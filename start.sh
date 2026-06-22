#!/bin/bash
# Costa Rica Travel - Main Start Script
set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

cleanup() {
  warn "Deteniendo servidores..."
  pkill -f "uvicorn app.main:app" 2>/dev/null || true
  pkill -f "node.*nuxt" 2>/dev/null || true
  info "Servidores detenidos"
}

trap cleanup EXIT INT TERM

kill_port() {
  local port=$1
  local pids=$(lsof -Pi :$port -sTCP:LISTEN -t 2>/dev/null)
  if [ -n "$pids" ]; then
    warn "Cerrando proceso en puerto $port (PID: $pids)..."
    kill -9 $pids 2>/dev/null || true
    sleep 1
  fi
}

echo "=========================================="
echo "  Costa Rica Travel - Inicio"
echo "=========================================="

# ─── Infrastructure ────────────────────────────────
if command -v docker &>/dev/null && docker compose version &>/dev/null; then
  if [ -f "$ROOT_DIR/docker-compose.infra.yml" ]; then
    info "Iniciando servicios de infraestructura..."
    docker compose -f "$ROOT_DIR/docker-compose.infra.yml" up -d 2>/dev/null || warn "Infraestructura ya estaba corriendo"
  fi
fi

# ─── Backend ───────────────────────────────────────
info "Iniciando backend..."
kill_port 8000

cd "$BACKEND_DIR"

if [ -d "venv" ]; then
  source venv/bin/activate
fi

mkdir -p uploads
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo "${BACKEND_PID}" > /tmp/costarica_backend.pid

for i in $(seq 1 30); do
  if curl -sf http://localhost:8000/health >/dev/null 2>&1; then
    info "Backend listo (PID: $BACKEND_PID)"
    break
  fi
  if [ "$i" -eq 30 ]; then
    error "Backend no pudo iniciar. Logs:"
    tail -10 /tmp/backend.log
    exit 1
  fi
  sleep 1
done

# ─── Sync passwords ────────────────────────────────
info "Sincronizando contraseñas de prueba..."
cd "$BACKEND_DIR"
source venv/bin/activate 2>/dev/null || true
python3 -c "
import asyncio
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.core.security import get_password_hash
from sqlalchemy import select

async def reset():
    async with AsyncSessionLocal() as session:
        for email in ['admin@costaricatravel.dev', 'superadmin@costaricatravel.dev', 'vendor@costaricatravel.dev', 'testclient@test.com']:
            result = await session.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()
            if user:
                user.password_hash = get_password_hash('Admin123!')
        await session.commit()
        print('  Contraseñas sincronizadas')
asyncio.run(reset())
" 2>/dev/null || warn "No se pudieron sincronizar contraseñas (ignorando)"

# ─── Frontend ──────────────────────────────────────
info "Iniciando frontend..."
kill_port 3000

cd "$FRONTEND_DIR"
npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "${FRONTEND_PID}" > /tmp/costarica_frontend.pid

for i in $(seq 1 60); do
  if curl -sf http://localhost:3000 >/dev/null 2>&1; then
    info "Frontend listo (PID: $FRONTEND_PID)"
    break
  fi
  if [ "$i" -eq 60 ]; then
    error "Frontend no pudo iniciar. Logs:"
    tail -10 /tmp/frontend.log
    exit 1
  fi
  sleep 1
done

echo ""
echo "=========================================="
echo "  ✅ SERVIDORES INICIADOS"
echo "=========================================="
echo ""
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "  Login:    http://localhost:3000/login"
echo ""
echo "  Credenciales:"
echo "    admin@costaricatravel.dev / Admin123!"
echo "    vendor@costaricatravel.dev / Admin123!"
echo "    testclient@test.com / Admin123!"
echo ""
echo "  Logs:"
echo "    Backend:  tail -f /tmp/backend.log"
echo "    Frontend: tail -f /tmp/frontend.log"
echo ""
echo "  Detener: pkill -f 'uvicorn|nuxt'"
echo "=========================================="

# Keep running if executed directly
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
  tail -f /tmp/backend.log /tmp/frontend.log 2>/dev/null &
  wait
fi
