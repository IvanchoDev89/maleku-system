# 🚀 Guía de Despliegue - Costa Rica Travel

Arquitectura recomendada: **Railway (Backend + DB) + Vercel (Frontend)**

## 📋 Pre-requisitos

- Cuenta en [Railway](https://railway.app)
- Cuenta en [Vercel](https://vercel.com)
- Cuenta en [GitHub](https://github.com)
- [Railway CLI](https://docs.railway.app/guides/cli) instalado: `npm install -g @railway/cli`
- [Vercel CLI](https://vercel.com/docs/cli) instalado: `npm install -g vercel`

---

## 🏗️ Paso 1: Configurar Backend en Railway

### 1.1 Crear proyecto en Railway

```bash
# Login a Railway
railway login

# Ir al directorio del backend
cd backend

# Inicializar proyecto
railway init
# Selecciona: "Create a new project"
# Nombre: "costarica-backend"
```

### 1.2 Agregar PostgreSQL

```bash
# En Railway dashboard o CLI
railway add --database postgres
# O usa el dashboard: New → Database → Add PostgreSQL
```

### 1.3 Agregar Redis

```bash
railway add --database redis
# O usa el dashboard: New → Database → Add Redis
```

### 1.4 Configurar Variables de Entorno

En el dashboard de Railway (Variables tab), agrega:

```env
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=tu-clave-secreta-aleatoria-min-32-caracteres
SITE_URL=https://tu-frontend-url.vercel.app
BACKEND_CORS_ORIGINS=["https://tu-frontend-url.vercel.app"]
RESEND_API_KEY=tu-api-key-de-resend
CLOUDINARY_CLOUD_NAME=tu-cloud-name
CLOUDINARY_API_KEY=tu-api-key
CLOUDINARY_API_SECRET=tu-api-secret
STRIPE_SECRET_KEY=sk_live_tu-key
STRIPE_PUBLISHABLE_KEY=pk_live_tu-key
```

**Nota:** Railway automáticamente inyecta `DATABASE_URL` y `REDIS_URL`

### 1.5 Desplegar Backend

```bash
# Desde el directorio backend
railway up

# Ejecutar migraciones
railway run alembic upgrade head
```

### 1.6 Obtener URL del Backend

```bash
railway domain
# Copia esta URL para configurar el frontend
```

---

## 🌐 Paso 2: Configurar Frontend en Vercel

### 2.1 Actualizar vercel.json

Edita `frontend/vercel.json` y reemplaza:
- `your-railway-app-url` → URL de Railway obtenida en paso 1.6
- `your-vercel-domain` → Tu dominio personalizado (opcional)

### 2.2 Configurar Variables de Entorno

```bash
cd frontend

# Login a Vercel
vercel login

# Link proyecto
vercel link
```

Variables en Vercel (Settings → Environment Variables):

```env
NUXT_PUBLIC_API_URL=https://tu-backend-url.up.railway.app/api/v1
NUXT_PUBLIC_SITE_URL=https://tu-frontend-url.vercel.app
```

### 2.3 Desplegar Frontend

```bash
vercel --prod
```

---

## ⚡ Despliegue Rápido (Script Automatizado)

```bash
# Desplegar solo backend
./deploy.sh backend

# Desplegar solo frontend
./deploy.sh frontend

# Desplegar todo
./deploy.sh all
```

---

## 🔧 Configuración Post-Deploy

### 1. Configurar Webhook de Stripe

En Stripe Dashboard → Webhooks:
- URL: `https://tu-backend.up.railway.app/api/v1/stripe/webhook`
- Events: `checkout.session.completed`, `invoice.paid`, etc.

### 2. Verificar Email (Resend)

En Resend Dashboard:
- Verificar dominio `costaricatravel.dev`
- Configurar SPF/DKIM records

### 3. Configurar Cloudinary

Verificar que las imágenes se suban correctamente desde producción.

---

## 📊 Monitoreo

### Railway Dashboard
- Logs en tiempo tiempo
- Métricas de CPU/Memoria
- Database metrics
- Alertas configurables

### Vercel Dashboard
- Analytics de tráfico
- Core Web Vitals
- Logs de funciones

---

## 🔄 CI/CD (Opcional)

### GitHub Actions para Railway

Crear `.github/workflows/deploy-backend.yml`:

```yaml
name: Deploy Backend

on:
  push:
    branches: [main]
    paths: ['backend/**']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: railway/cli@v2
        with:
          railway_token: ${{ secrets.RAILWAY_TOKEN }}
      - run: cd backend && railway up
```

### GitHub Actions para Vercel

Vercel ya tiene integración automática con GitHub. Solo conecta tu repo.

---

## 💰 Costos Estimados (Producción)

| Servicio | Plan | Costo/Mes |
|----------|------|-----------|
| Railway | Pro (2 vCPU, 4GB) | $20 |
| Railway Postgres | Pro (10GB) | Incluido |
| Railway Redis | Incluido | $0 |
| Vercel | Pro | $20 |
| **Total** | | **$40/mes** |

---

## 🆘 Troubleshooting

### Backend no inicia
```bash
# Ver logs
railway logs

# Verificar variables
railway variables

# Shell interactivo
railway run bash
```

### Error de CORS
- Verificar `BACKEND_CORS_ORIGINS` incluye URL de Vercel
- No olvidar `https://` y sin trailing slash

### Database connection error
- Railway inyecta `DATABASE_URL` automáticamente
- No sobrescribir en variables manuales

### Frontend no conecta a backend
- Verificar `NUXT_PUBLIC_API_URL` en Vercel
- Probar endpoint: `curl https://backend-url.up.railway.app/health`

---

## 📞 Soporte

- Railway: [docs.railway.app](https://docs.railway.app) + Discord
- Vercel: [vercel.com/docs](https://vercel.com/docs) + Support
- Costa Rica Travel: Abrir issue en GitHub
