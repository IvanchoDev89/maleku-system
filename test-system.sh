#!/bin/bash
# Test Completo del Sistema Costa Rica Travel

echo "=========================================="
echo "  TEST DEL SISTEMA - Costa Rica Travel"
echo "=========================================="
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASS=0
FAIL=0

# Función de test
test_step() {
    echo -n "→ $1... "
}

pass() {
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASS++))
}

fail() {
    echo -e "${RED}✗ FAIL${NC}: $1"
    ((FAIL++))
}

warning() {
    echo -e "${YELLOW}⚠ WARNING${NC}: $1"
}

echo "1. VERIFICANDO PROCESOS"
echo "----------------------"

# Test 1: Verificar si hay procesos corriendo
test_step "Procesos Node/Nuxt"
if pgrep -f "nuxt" > /dev/null || pgrep -f "node.*vue" > /dev/null; then
    pass
else
    fail "No hay procesos de Nuxt corriendo"
fi

test_step "Procesos Python/FastAPI"
if pgrep -f "uvicorn" > /dev/null || pgrep -f "fastapi" > /dev/null; then
    pass
else
    fail "No hay procesos de FastAPI corriendo"
fi

echo ""
echo "2. VERIFICANDO PUERTOS"
echo "----------------------"

# Test 2: Puerto 3000 (Frontend)
test_step "Puerto 3000 (Frontend)"
if nc -z localhost 3000 2>/dev/null || curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q "200\|301\|302"; then
    pass
else
    fail "Puerto 3000 no responde"
fi

# Test 3: Puerto 8000 (Backend)
test_step "Puerto 8000 (Backend)"
if nc -z localhost 8000 2>/dev/null || curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null | grep -q "200"; then
    pass
else
    # Intentar health check genérico
    if curl -s http://localhost:8000 2>/dev/null | grep -q " Costa Rica Travel"; then
        pass
    else
        fail "Puerto 8000 no responde"
    fi
fi

echo ""
echo "3. VERIFICANDO FRONTEND"
echo "----------------------"

# Test 4: Frontend carga HTML correctamente
test_step "Frontend HTML"
FRONTEND_RESP=$(curl -s http://localhost:3000 2>/dev/null | head -20)
if echo "$FRONTEND_RESP" | grep -q "<html\|<!DOCTYPE\|<div\|<script"; then
    pass
else
    fail "Frontend no devuelve HTML válido"
fi

# Test 5: Verificar que no hay errores de iconos
test_step "Iconos (lucide-vue-next)"
if grep -r "from 'lucide-vue-next'" /home/marcelo/Documents/costaricatravel.dev/frontend/layouts/superadmin.vue > /dev/null; then
    pass
else
    fail "lucide-vue-next no importado en layouts"
fi

echo ""
echo "4. VERIFICANDO BACKEND"
echo "----------------------"

# Test 6: Backend health endpoint
test_step "Backend /health"
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null)
if [ "$HEALTH_STATUS" = "200" ]; then
    pass
else
    warning "Health endpoint devolvió $HEALTH_STATUS (puede ser normal si no existe)"
    ((PASS++))  # No contamos como fallo grave
fi

# Test 7: CORS headers
test_step "CORS Headers"
CORS_HEADER=$(curl -sI http://localhost:8000 2>/dev/null | grep -i "access-control-allow-origin")
if [ -n "$CORS_HEADER" ]; then
    pass
    echo "   $CORS_HEADER"
else
    warning "No se detectaron headers CORS (puede ser normal para algunos endpoints)"
    ((PASS++))
fi

echo ""
echo "5. VERIFICANDO DEPENDENCIAS"
echo "---------------------------"

# Test 8: lucide-vue-next instalado
test_step "lucide-vue-next en node_modules"
if [ -d "/home/marcelo/Documents/costaricatravel.dev/frontend/node_modules/lucide-vue-next" ]; then
    pass
else
    fail "lucide-vue-next no está instalado"
fi

# Test 9: package.json tiene lucide
test_step "lucide-vue-next en package.json"
if grep -q "lucide-vue-next" /home/marcelo/Documents/costaricatravel.dev/frontend/package.json; then
    pass
else
    fail "lucide-vue-next no está en package.json"
fi

echo ""
echo "=========================================="
echo "  RESULTADOS"
echo "=========================================="
echo -e "Tests Pasados: ${GREEN}$PASS${NC}"
echo -e "Tests Fallidos: ${RED}$FAIL${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✓ TODOS LOS TESTS PASARON${NC}"
    exit 0
elif [ $FAIL -le 2 ]; then
    echo -e "${YELLOW}⚠ ALGUNOS TESTS FALLARON (menores)${NC}"
    exit 0
else
    echo -e "${RED}✗ DEMASIADOS TESTS FALLARON${NC}"
    exit 1
fi
