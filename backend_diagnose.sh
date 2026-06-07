#!/bin/bash
set -e

echo "=== Backend Diagnostics ==="
cd /home/marcelo/Documents/costaricatravel.dev/backend

# Check Python
echo "Python version:"
source venv/bin/activate
python --version

# Check if can import app
echo ""
echo "Testing app import..."
python -c "from app.main import app; print('App imports OK')" 2>&1 || echo "IMPORT FAILED"

# Check config
echo ""
echo "Config check..."
python -c "from app.core.config import settings; print(f'DEBUG={settings.DEBUG}'); print(f'DB={settings.DATABASE_URL[:50]}...')" 2>&1 || echo "CONFIG FAILED"

# Check database file
echo ""
echo "Database files:"
ls -la *.db 2>/dev/null || echo "No .db files in root"
ls -la data/*.db 2>/dev/null || echo "No .db files in data/"

# Check processes
echo ""
echo "Uvicorn processes:"
ps aux | grep uvicorn | grep -v grep || echo "No uvicorn running"

echo ""
echo "Port 8000:"
netstat -tlnp 2>/dev/null | grep 8000 || ss -tlnp 2>/dev/null | grep 8000 || echo "Port 8000 not in use"

echo ""
echo "=== Diagnostics Complete ==="
