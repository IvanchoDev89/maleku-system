#!/bin/bash
# Script para iniciar todos los servicios - Costa Rica Travel

echo "=========================================="
echo "Iniciando Costa Rica Travel - Full Stack"
echo "=========================================="

# 1. Configurar PostgreSQL
echo ""
echo "[1/4] Configurando PostgreSQL..."
sudo bash -c 'cat > /etc/postgresql/16/main/pg_hba.conf << "EOF"
# PostgreSQL Client Authentication Configuration File
local   all             all                                     trust
host    all             all             127.0.0.1/32            trust
host    all             all             ::1/128                 trust
host    all             all             0.0.0.0/0               trust
EOF'

sudo service postgresql restart
sleep 3

# Crear base de datos si no existe
sudo -u postgres psql -c "CREATE DATABASE costaricatravel;" 2>/dev/null || echo "Database already exists or error"

# 2. Detener procesos previos
echo ""
echo "[2/4] Deteniendo procesos previos..."
pkill -f uvicorn 2>/dev/null
pkill -f "node.*nuxt" 2>/dev/null
sleep 2

# 3. Iniciar Backend
echo ""
echo "[3/4] Iniciando Backend (FastAPI) en http://localhost:8000..."
cd /home/marcelo/Documents/costaricatravel.dev/backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Esperar a que el backend esté listo
echo "Esperando backend..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        echo "✅ Backend listo!"
        break
    fi
    sleep 1
    echo -n "."
done

# 4. Iniciar Frontend
echo ""
echo "[4/4] Iniciando Frontend (Nuxt) en http://localhost:3000..."
cd /home/marcelo/Documents/costaricatravel.dev/frontend
rm -rf .nuxt 2>/dev/null
PORT=3000 npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

# Esperar a que el frontend esté listo
echo "Esperando frontend..."
for i in {1..30}; do
    if curl -s http://localhost:3000 >/dev/null 2>&1; then
        echo "✅ Frontend listo!"
        break
    fi
    sleep 1
    echo -n "."
done

echo ""
echo "=========================================="
echo "✅ Todos los servicios iniciados!"
echo "=========================================="
echo ""
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Para ver logs:"
echo "  Backend:  tail -f /tmp/backend.log"
echo "  Frontend: tail -f /tmp/frontend.log"
echo ""
echo "Para detener:"
echo "  pkill -f uvicorn; pkill -f 'node.*nuxt'"
echo ""

# Verificar que todo funciona
echo "Verificando servicios..."
echo ""
echo "Backend Health Check:"
curl -s http://localhost:8000/health 2>/dev/null || echo "❌ Backend no responde"

echo ""
echo "Backend Newsletter API:"
curl -s -X POST http://localhost:8000/api/v1/newsletter/subscribe \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","first_name":"Test"}' 2>/dev/null || echo "❌ Newsletter API no responde"

echo ""
echo "Frontend:"
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null || echo "❌ Frontend no responde"

echo ""
echo "Done!"
