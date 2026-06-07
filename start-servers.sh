#!/bin/bash
# Script para iniciar servidores de desarrollo
# Costa Rica Travel Platform

echo "🚀 Iniciando servidores de Costa Rica Travel..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para verificar si un puerto está en uso
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Función para matar procesos en un puerto
kill_port() {
    local port=$1
    local pids=$(lsof -Pi :$port -sTCP:LISTEN -t 2>/dev/null)
    if [ ! -z "$pids" ]; then
        echo -e "${YELLOW}Matando procesos en puerto $port...${NC}"
        kill -9 $pids 2>/dev/null
        sleep 2
    fi
}

# Directorio base
BASE_DIR="/home/marcelo/Documents/costaricatravel.dev"

# ============================================
# DETENER SERVIDORES EXISTENTES
# ============================================
echo -e "${YELLOW}Deteniendo servidores existentes...${NC}"

kill_port 8000
# kill_port 3003 - ya no usamos este puerto
kill_port 3000

pkill -9 -f "uvicorn" 2>/dev/null
pkill -9 -f "nuxt" 2>/dev/null
pkill -9 -f "node.*nuxt" 2>/dev/null

sleep 3

# ============================================
# INICIAR BACKEND
# ============================================
echo -e "${GREEN}Iniciando Backend (FastAPI)...${NC}"
cd "$BASE_DIR/backend"

# Verificar virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Iniciar backend en background
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > /tmp/backend.log 2>&1 &
BACKEND_PID=$!

echo -e "${GREEN}Backend iniciado con PID: $BACKEND_PID${NC}"

# Esperar a que backend esté listo
echo -n "Esperando backend..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health >/dev/null 2>&1 || curl -s http://localhost:8000/ >/dev/null 2>&1; then
        echo -e " ${GREEN}✅ Listo!${NC}"
        break
    fi
    echo -n "."
    sleep 1
done

# Verificar si backend está corriendo
if ! ps -p $BACKEND_PID > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: Backend no pudo iniciar${NC}"
    echo "Logs del backend:"
    tail -20 /tmp/backend.log
    exit 1
fi

# ============================================
# INICIAR FRONTEND
# ============================================
echo -e "${GREEN}Iniciando Frontend (Nuxt)...${NC}"
cd "$BASE_DIR/frontend"

# Iniciar frontend en background
nohup npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!

echo -e "${GREEN}Frontend iniciado con PID: $FRONTEND_PID${NC}"

# Esperar a que frontend esté listo
echo -n "Esperando frontend..."
for i in {1..60}; do
    if curl -s http://localhost:3000 >/dev/null 2>&1; then
        echo -e " ${GREEN}✅ Listo!${NC}"
        break
    fi
    echo -n "."
    sleep 1
done

# ============================================
# RESUMEN
# ============================================
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   SERVIDORES INICIADOS CORRECTAMENTE   ${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "🌐 Frontend: ${GREEN}http://localhost:3000${NC}"
echo -e "🔌 Backend:  ${GREEN}http://localhost:8000${NC}"
echo -e "📚 API Docs: ${GREEN}http://localhost:8000/docs${NC}"
echo ""
echo -e "🔗 URLs importantes:"
echo -e "   - Login:           http://localhost:3000/login"
echo -e "   - Super Admin:     http://localhost:3000/superadmin/dashboard"
echo -e "   - API Health:      http://localhost:8000/health"
echo ""
echo -e "📋 Para detener los servidores:"
echo -e "   ${YELLOW}pkill -9 -f 'uvicorn|nuxt'${NC}"
echo ""
echo -e "📄 Logs:"
echo -e "   Backend:  ${YELLOW}tail -f /tmp/backend.log${NC}"
echo -e "   Frontend: ${YELLOW}tail -f /tmp/frontend.log${NC}"
echo ""

# Guardar PIDs para referencia
echo "$BACKEND_PID" > /tmp/costa_rica_backend.pid
echo "$FRONTEND_PID" > /tmp/costa_rica_frontend.pid

# Mantener script corriendo si se ejecutó directamente
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    echo -e "${GREEN}Presiona Ctrl+C para detener el seguimiento${NC}"
    echo -e "${YELLOW}(Los servidores seguirán corriendo en background)${NC}"
    echo ""
    
    # Mostrar logs en tiempo real
    tail -f /tmp/backend.log /tmp/frontend.log 2>/dev/null &
    TAIL_PID=$!
    
    # Esperar Ctrl+C
    trap "kill $TAIL_PID 2>/dev/null; exit 0" INT
    wait
fi
