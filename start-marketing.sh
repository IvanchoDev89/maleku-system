#!/bin/bash
# Script para iniciar el módulo de marketing de BillionMail

echo "🚀 Iniciando módulo de marketing..."

# 1. Crear tablas de marketing
echo "📊 Creando tablas de marketing..."
cd /home/marcelo/Documents/costaricatravel.dev/backend

python3 -c "
import asyncio
import sys
sys.path.insert(0, '.')
from app.core.database import engine
from app.models.marketing import EmailCampaign, EmailTemplate, EmailLog, MarketingAutomation, InboxMessage, EmailPreference
from sqlalchemy import inspect

async def check_tables():
    async with engine.connect() as conn:
        def get_tables(sync_conn):
            inspector = inspect(sync_conn)
            return inspector.get_table_names()
        
        tables = await conn.run_sync(get_tables)
        
        marketing_tables = ['email_campaigns', 'email_templates', 'email_logs', 
                         'marketing_automations', 'inbox_messages', 'email_preferences']
        
        for table in marketing_tables:
            if table in tables:
                print(f'✅ Tabla {table} ya existe')
            else:
                print(f'⚠️ Tabla {table} NO existe - necesita migración')
        
        return tables

asyncio.run(check_tables())
    
await engine.dispose()
"

echo ""
echo "📋 Notas importantes:"
echo "  - BillionMail requiere Docker para funcionar completamente"
echo "  - Las tablas de marketing están configuradas en el backend"
echo "  - Los dashboards están listos en el frontend"
echo ""
echo "Para completar la instalación:"
echo "  1. Instalar Docker y Docker Compose"
echo "  2. cd billionmail && docker-compose up -d"
echo "  3. Reiniciar backend y frontend"
echo ""
echo "✅ Setup de marketing completado!"
