#!/usr/bin/env bash
# =============================================================================
# Smoke Test: Flujo completo de reservas
# =============================================================================
# Usage:  bash tests/test_reservation_flow.sh [BASE_URL]
#
# Usa fechas dinámicas (siempre 60 días en el futuro) para evitar
# conflictos con reservas de ejecuciones anteriores.
# =============================================================================

set -euo pipefail

BASE="${1:-http://localhost:8000}"
API="$BASE/api/v1"
PASS=0
FAIL=0

GREEN='\033[0;32m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

# Helpers
check_contains() {
    local test_name="$1" expected="$2" actual="$3"
    if echo "$actual" | grep -q "$expected"; then
        echo -e "  ${GREEN}✓ PASS${NC} $test_name"
        PASS=$((PASS + 1))
    else
        echo -e "  ${RED}✗ FAIL${NC} $test_name"
        echo -e "    ${RED}expected to contain: $expected${NC}"
        FAIL=$((FAIL + 1))
    fi
}

json_val() {
    echo "$1" | python3 -c "import json,sys; print(json.load(sys.stdin).get('$2',''))" 2>/dev/null || echo ""
}

json_str() {
    echo "$1" | python3 -c "import json,sys; v=json.load(sys.stdin).get('$2',''); print(json.dumps(v))" 2>/dev/null || echo '""'
}

# Generate future dates using hour+minute as seed so each minute gets unique dates
# This avoids collisions between consecutive runs
NOW=$(date +%s)
MINUTE_SEED=$((NOW / 60))                # changes every minute
OFFSET_DAYS=$((90 + (MINUTE_SEED % 60))) # 90-149 days, changes every minute
OFFSET=$((OFFSET_DAYS * 24 * 60 * 60))
CI_TS=$((NOW + OFFSET))
CO_TS=$((CI_TS + 3 * 24 * 60 * 60))     # +3 nights
CI_DATE=$(date -d "@$CI_TS" +%Y-%m-%d)
CO_DATE=$(date -d "@$CO_TS" +%Y-%m-%d)
CI_ISO="${CI_DATE}T00:00:00Z"
CO_ISO="${CO_DATE}T00:00:00Z"

echo ""
echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}  Smoke Test: Flujo Completo de Reservas${NC}"
echo -e "${CYAN}============================================${NC}"
echo -e "  Fechas de prueba: $CI_DATE → $CO_DATE"
echo ""

# ─── 1. Health Check ───────────────────────────────────────────
echo -e "${CYAN}[1/12] Health Check${NC}"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$BASE/health" 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "  ${GREEN}✓ PASS${NC} Backend health endpoint"; PASS=$((PASS + 1))
else
    echo -e "  ${RED}✗ FAIL${NC} Backend health (got $HTTP_CODE)"; FAIL=$((FAIL + 1))
fi

# ─── 2. Properties List ────────────────────────────────────────
echo ""
echo -e "${CYAN}[2/12] Listar propiedades${NC}"
PROPS=$(curl -s --max-time 10 "$API/properties?limit=3" 2>/dev/null || echo '{}')
check_contains "Response has items" '"items"' "$PROPS"

# ─── 3. Property Detail by Slug ─────────────────────────────────
echo ""
echo -e "${CYAN}[3/12] Detalle de propiedad por slug${NC}"
DETAIL=$(curl -s --max-time 10 "$API/properties/slug/hotel-tamarindo" 2>/dev/null || echo '{}')
check_contains "Response has name" '"name"' "$DETAIL"
check_contains "Response has rooms" '"rooms"' "$DETAIL"
check_contains "Response has vendor" '"vendor"' "$DETAIL"
PROP_ID=$(json_val "$DETAIL" "id")
# Extract all room IDs into an array
ROOM_JSON=$(echo "$DETAIL" | python3 -c "
import json,sys
d=json.load(sys.stdin)
rooms = d.get('rooms',[])
for r in rooms:
    print(r['id'], r['name'], r['price_per_night'])
" 2>/dev/null || echo "")
ROOM_COUNT=$(echo "$ROOM_JSON" | wc -l)
echo "       Habitaciones: $ROOM_COUNT"

# ─── 4. Login como cliente ──────────────────────────────────────
echo ""
echo -e "${CYAN}[4/12] Login como cliente${NC}"
LOGIN_RESP=$(curl -s -X POST --max-time 10 "$API/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"testclient@test.com","password":"Admin123!"}' 2>/dev/null || echo '{}')
CLIENT_TOKEN=$(json_val "$LOGIN_RESP" "access_token")
if [ -n "$CLIENT_TOKEN" ]; then
    echo -e "  ${GREEN}✓ PASS${NC} Login cliente exitoso"; PASS=$((PASS + 1))
else
    echo -e "  ${RED}✗ FAIL${NC} Login cliente falló"; FAIL=$((FAIL + 1))
fi

# ─── 5. Login como vendor ────────────────────────────────────────
echo ""
echo -e "${CYAN}[5/12] Login como vendor${NC}"
VENDOR_LOGIN=$(curl -s -X POST --max-time 10 "$API/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"vendor@costaricatravel.dev","password":"Admin123!"}' 2>/dev/null || echo '{}')
VENDOR_TOKEN=$(json_val "$VENDOR_LOGIN" "access_token")
if [ -n "$VENDOR_TOKEN" ]; then
    echo -e "  ${GREEN}✓ PASS${NC} Login vendor exitoso"; PASS=$((PASS + 1))
else
    echo -e "  ${RED}✗ FAIL${NC} Login vendor falló"; FAIL=$((FAIL + 1))
fi

# ─── 6. Find available room for selected dates ──────────────────
echo ""
echo -e "${CYAN}[6/12] Buscar habitación disponible${NC}"
# Iterate through rooms until we find one available for our dates
ROOM_ID=""
BOOK_CI_ISO="$CI_ISO"
BOOK_CO_ISO="$CO_ISO"
BOOK_CI="$CI_DATE"
BOOK_CO="$CO_DATE"

while IFS= read -r line; do
    [ -z "$line" ] && continue
    RID=$(echo "$line" | awk '{print $1}')
    RNAME=$(echo "$line" | awk '{$1=""; print $0}' | xargs)
    CHECK=$(curl -s -X POST --max-time 10 "$API/availability/rooms/check" \
        -H "Content-Type: application/json" \
        -d "{\"room_id\": \"$RID\", \"check_in\": \"$CI_ISO\", \"check_out\": \"$CO_ISO\"}" 2>/dev/null || echo '{}')
    IS_AVAIL=$(echo "$CHECK" | python3 -c "import json,sys; print(json.load(sys.stdin).get('available',''))" 2>/dev/null || echo "")
    if [ "$IS_AVAIL" = "True" ] || [ "$IS_AVAIL" = "true" ]; then
        ROOM_ID="$RID"
        echo "       ✓ $RNAME ($RID) disponible para $CI_DATE → $CO_DATE"
        break
    fi
    echo "       ✗ $RNAME no disponible, probando siguiente..."
done <<< "$ROOM_JSON"

if [ -z "$ROOM_ID" ]; then
    # Fallback: use next-available to find any date range for the first room
    FIRST_RID=$(echo "$ROOM_JSON" | head -1 | awk '{print $1}')
    echo "       Buscando próximas fechas disponibles..."
    NEXT_RANGES=$(curl -s --max-time 10 "$API/availability/rooms/$FIRST_RID/next-available?nights=3" 2>/dev/null || echo '{}')
    BK_CI=$(echo "$NEXT_RANGES" | python3 -c "
import json,sys
ranges = json.load(sys.stdin).get('available_ranges',[])
for r in ranges:
    ci = r.get('check_in','')[:10]
    # skip past dates
    import datetime
    today = datetime.date.today()
    if ci >= str(today):
        print(ci)
        break
" 2>/dev/null || echo "")
    if [ -n "$BK_CI" ] && [ "$BK_CI" != "None" ]; then
        BK_CO=$(echo "$NEXT_RANGES" | python3 -c "
import json,sys
ranges = json.load(sys.stdin).get('available_ranges',[])
for r in ranges:
    ci = r.get('check_in','')[:10]
    import datetime
    today = datetime.date.today()
    if ci >= str(today):
        print(r.get('check_out','')[:10])
        break
" 2>/dev/null || echo "")
        ROOM_ID="$FIRST_RID"
        BOOK_CI="${BK_CI}"
        BOOK_CO="${BK_CO}"
        BOOK_CI_ISO="${BK_CI}T00:00:00Z"
        BOOK_CO_ISO="${BK_CO}T00:00:00Z"
        echo "       Usando fecha alternativa: $BOOK_CI → $BOOK_CO (room $FIRST_RID)"
    fi
fi

if [ -n "$ROOM_ID" ]; then
    echo -e "  ${GREEN}✓ PASS${NC} Habitación disponible encontrada"; PASS=$((PASS + 1))
else
    echo -e "  ${RED}✗ FAIL${NC} No hay habitaciones disponibles"; FAIL=$((FAIL + 1))
fi

# ─── 7. Price Preview ───────────────────────────────────────────
echo ""
echo -e "${CYAN}[7/12] Previsualización de precio${NC}"
PREVIEW=$(curl -s -X POST --max-time 10 "$API/bookings/preview" \
    -H "Authorization: Bearer $CLIENT_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"room_id\": \"$ROOM_ID\", \"check_in\": \"$BOOK_CI_ISO\", \"check_out\": \"$BOOK_CO_ISO\", \"guests\": 2}" 2>/dev/null || echo '{}')
check_contains "Has subtotal" '"subtotal"' "$PREVIEW"
check_contains "Has total" '"total"' "$PREVIEW"
check_contains "Has nights" '"nights"' "$PREVIEW"
echo "       Total estimado: \$$(json_val "$PREVIEW" "total")"

# ─── 8. Calendar ────────────────────────────────────────────────
echo ""
echo -e "${CYAN}[8/12] Calendario de disponibilidad${NC}"
CALENDAR=$(curl -s --max-time 10 "$API/availability/rooms/$ROOM_ID/calendar?start_date=${BOOK_CI_ISO}&days=31" 2>/dev/null || echo '{}')
check_contains "Has room_id" '"room_id"' "$CALENDAR"
check_contains "Has dates" '"dates"' "$CALENDAR"

# ─── 9. Next Available ──────────────────────────────────────────
echo ""
echo -e "${CYAN}[9/12] Próximas fechas disponibles${NC}"
NEXT=$(curl -s --max-time 10 "$API/availability/rooms/$ROOM_ID/next-available?nights=3" 2>/dev/null || echo '{}')
check_contains "Has available_ranges" '"available_ranges"' "$NEXT"

# ─── 10. Vendor: bloquear fechas ─────────────────────────────────
echo ""
echo -e "${CYAN}[10/12] Vendor: bloquear fechas en calendario${NC}"
BLOCK_DATE_TS=$(( $(date -d "$BOOK_CI" +%s) + 86400 * 10 ))  # 10 days after booking check-in
BLOCK_DATE=$(date -d "@$BLOCK_DATE_TS" +%Y-%m-%d)
CAL_PUT=$(curl -s -X PUT --max-time 10 "$API/availability/rooms/$ROOM_ID/calendar" \
    -H "Authorization: Bearer $VENDOR_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"entries\": [{\"date\": \"$BLOCK_DATE\", \"is_available\": false, \"notes\": \"Bloqueado\"}]}" 2>/dev/null || echo '{}')
check_contains "Calendar updated" '"updated_count"' "$CAL_PUT"
echo "       Fecha bloqueada: $BLOCK_DATE"

# ─── 11. Crear reserva (fechas futuras confirmadas disponibles) ──
echo ""
echo -e "${CYAN}[11/12] Crear reserva de propiedad${NC}"
BOOKING=$(curl -s -X POST --max-time 10 "$API/bookings/property" \
    -H "Authorization: Bearer $CLIENT_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"property_id\": \"$PROP_ID\", \"room_id\": \"$ROOM_ID\", \"check_in\": \"$BOOK_CI_ISO\", \"check_out\": \"$BOOK_CO_ISO\", \"guests\": 2, \"guest_name\": \"Smoke Test\", \"guest_email\": \"smoke@test.com\", \"guest_phone\": \"+50670000000\"}" 2>/dev/null || echo '{}')
BOOKING_ID=$(json_val "$BOOKING" "id")
if [ -n "$BOOKING_ID" ]; then
    echo -e "  ${GREEN}✓ PASS${NC} Reserva creada (ID: ${BOOKING_ID:0:8}...)"; PASS=$((PASS + 1))
    STATUS=$(json_val "$BOOKING" "status")
    if [ "$STATUS" = "pending" ]; then
        echo -e "  ${GREEN}✓ PASS${NC} Status is pending"; PASS=$((PASS + 1))
    else
        echo -e "  ${RED}✗ FAIL${NC} Status esperado: pending, obtenido: $STATUS"; FAIL=$((FAIL + 1))
    fi
    BOOKING_TYPE=$(json_val "$BOOKING" "booking_type")
    if [ "$BOOKING_TYPE" = "property" ]; then
        echo -e "  ${GREEN}✓ PASS${NC} Is property booking"; PASS=$((PASS + 1))
    else
        echo -e "  ${RED}✗ FAIL${NC} Tipo esperado: property, obtenido: $BOOKING_TYPE"; FAIL=$((FAIL + 1))
    fi
else
    echo -e "  ${RED}✗ FAIL${NC} No se pudo crear la reserva"
    echo "       Response: $(echo "$BOOKING" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('detail',''))" 2>/dev/null || head -c 200)"
    FAIL=$((FAIL + 3))
fi

# ─── 12. Verificar que la reserva bloquea disponibilidad ─────────
echo ""
echo -e "${CYAN}[12/12] Verificar bloqueo por reserva${NC}"
BLOCKED_CHECK=$(curl -s -X POST --max-time 10 "$API/availability/rooms/check" \
    -H "Content-Type: application/json" \
    -d "{\"room_id\": \"$ROOM_ID\", \"check_in\": \"$BOOK_CI_ISO\", \"check_out\": \"$BOOK_CO_ISO\"}" 2>/dev/null || echo '{}')
IS_AVAIL=$(json_val "$BLOCKED_CHECK" "available")
if [ "$IS_AVAIL" = "False" ] || [ "$IS_AVAIL" = "false" ]; then
    echo -e "  ${GREEN}✓ PASS${NC} Disponibilidad bloqueada correctamente"; PASS=$((PASS + 1))
else
    echo -e "  ${RED}✗ FAIL${NC} Debería estar bloqueada (available=$IS_AVAIL)"; FAIL=$((FAIL + 1))
fi

# ─── Summary ─────────────────────────────────────────────────────
echo ""
echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}  Resultados${NC}"
echo -e "${CYAN}============================================${NC}"
echo -e "  ${GREEN}PASS: $PASS${NC}"
echo -e "  ${RED}FAIL: $FAIL${NC}"
TOTAL=$((PASS + FAIL))
echo -e "  Total: $TOTAL"

if [ "$FAIL" -eq 0 ]; then
    echo -e "\n  ${GREEN}✓ Todos los tests pasaron${NC}"
else
    echo -e "\n  ${RED}✗ $FAIL test(s) fallaron${NC}"
fi
echo ""
