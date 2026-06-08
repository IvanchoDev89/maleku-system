<p align="center">
  <img src="https://raw.githubusercontent.com/your-org/costarica-travel/main/frontend/public/logo.svg" alt="Costa Rica Travel Logo" width="200">
</p>

<h1 align="center">Costa Rica Travel</h1>

<p align="center">
  <strong>Plataforma de turismo multi-vendor para Costa Rica</strong>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#demo">Demo</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#api">API</a> •
  <a href="#deployment">Deployment</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Nuxt.js-00DC82?style=for-the-badge&logo=nuxtdotjs&logoColor=white" alt="Nuxt.js">
  <img src="https://img.shields.io/badge/PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white" alt="Redis">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
</p>

---

## 🌟 Features

### Core Features
- ✅ **Multi-vendor Marketplace** - Vendors pueden registrar hoteles, tours, vehículos, botes, vuelos
- ✅ **Sistema de Reservas** - Booking engine con calendario de disponibilidad
- ✅ **Autenticación JWT** - Login seguro con refresh tokens y rate limiting
- ✅ **Búsqueda Full-text** - PostgreSQL tsvector para búsqueda rápida
- ✅ **Multi-idioma** - Español, Inglés y Francés (i18n)
- ✅ **Responsive Design** - Mobile-first con Tailwind CSS
- ✅ **SEO Optimizado** - Meta tags, Open Graph, sitemap.xml

### Vendor Features
- 📊 Dashboard con analytics
- 🏨 Gestión de propiedades (hoteles, tours, vehículos)
- 📅 Calendario de disponibilidad
- 💰 Sistema de comisiones (10% por defecto)
- ⭐ Sistema de reviews y ratings

### Admin Features
- 👥 Gestión de usuarios y vendors
- 📝 CMS para blog y destinos
- 📧 Email marketing automation
- 🔒 RBAC con 4 roles (Super Admin, Admin, Vendor, Client)

### Security
- 🔐 Password hashing con bcrypt
- 🛡️ Rate limiting (60 req/min)
- 🚫 CORS configurado
- 📝 Audit logging
- 🔑 JWT con blacklist

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                         CLIENTS                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Web App   │  │  Mobile App │  │   Admin     │         │
│  │  (Nuxt.js)  │  │   (Future)  │  │   Panel     │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
└─────────┼────────────────┼────────────────┼───────────────┘
          │                │                │
          └────────────────┴────────────────┘
                           │ HTTPS
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      VERCEL (Edge)                          │
│                    Nuxt.js 3 Frontend                       │
│  - SSR/SSG  - i18n  - Tailwind  - Pinia                     │
└──────────────────────┬──────────────────────────────────────┘
                       │ API Calls
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                     RAILWAY (Containers)                    │
│                   FastAPI Backend                           │
┌──────────────┬──────────────┬───────────────────────────────┐│
│   API Layer  │   Service    │     Repository               ││
│   (FastAPI)  │    Layer     │      Layer                  ││
└──────┬───────┴──────┬───────┴────────┬──────────────────────┘│
       │              │                │                       │
       ▼              ▼                ▼                       │
┌─────────────┐ ┌─────────────┐ ┌─────────────────┐             │
│  PostgreSQL │ │    Redis    │ │   Cloudinary    │             │
│  (Neon/     │ │  (Upstash/  │ │   (Images)      │             │
│  Railway)   │ │  Railway)   │ │                 │             │
└─────────────┘ └─────────────┘ └─────────────────┘             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local frontend dev)
- Python 3.11+ (for local backend dev)

### Option 1: Docker (Recommended)

```bash
# 1. Clone repository
git clone https://github.com/your-org/costa-rica-travel.git
cd costa-rica-travel

# 2. Copy environment variables
cp backend/.env.example backend/.env
# Edit backend/.env with your secrets

# 3. Start all services
docker-compose up -d

# 4. Run migrations
docker-compose exec api alembic upgrade head

# 5. Access services
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Local Development

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
# Configure .env
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
# Configure .env
npm run dev
```

### Option 3: Hybrid Mode (DBs already running)

If you already have PostgreSQL/Redis running (e.g. via `docker run` or system services), you can run only MailHog via docker and use native processes for the rest. This gives instant hot-reload:

```bash
# 1. MailHog only (for email capture in dev)
docker run -d --name costarica_mailhog \
  -p 1025:1025 -p 8025:8025 \
  mailhog/mailhog:latest

# 2. Use existing PostgreSQL + Redis (configure backend/.env)
# DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5434/costaricatravel
# REDIS_URL=redis://localhost:6381/0
# SMTP_HOST=localhost  # for native backend → mailhog
# SMTP_HOST=mailhog    # for dockerized backend → mailhog

# 3. Alembic stamp (skip if DB already has tables from a prior run)
cd backend && alembic stamp head

# 4. Seed (idempotent)
python3 -m app.scripts.seed_costa_rica

# 5. Start backend
cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000

# 6. Start frontend
cd frontend && npm run dev

# 7. Access
# Frontend:  http://localhost:3000
# API:       http://localhost:8000/docs
# MailHog:   http://localhost:8025  (catches all outgoing emails)
```

### Stripe Webhooks (Test Mode)

Local webhooks need the Stripe CLI forwarder:

```bash
# Install: https://stripe.com/docs/stripe-cli
stripe login
stripe listen --forward-to localhost:8000/api/v1/stripe/webhook
# Copy the printed signing secret (whsec_...) into STRIPE_WEBHOOK_SECRET in backend/.env
# Then trigger a test event:
stripe trigger checkout.session.completed
```

---

## 📊 Database Schema

### Core Entities
```
User (Auth)
├── Vendor (Business Profile)
│   ├── Property (Hotels)
│   ├── Tour
│   ├── Vehicle
│   ├── Boat
│   └── Flight
├── Booking (Reservations)
├── Review (Ratings)
└── Conversation (Chat)

BlogPost (CMS)
Destination (Guides)
Marketing (Campaigns)
```

### Key Features
- **Soft Delete** - Todos los modelos tienen `deleted_at`
- **JSONB** - Campos flexibles para features/aménities
- **Full-text Search** - Índices GIN para búsqueda
- **Audit Logs** - Tracking de cambios

---

## 🔌 API Endpoints

### Authentication
```
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/refresh
POST /api/v1/auth/logout
POST /api/v1/auth/forgot-password
POST /api/v1/auth/reset-password
POST /api/v1/auth/verify-email
GET  /api/v1/auth/me
```

### Users
```
GET    /api/v1/users/me
PUT    /api/v1/users/me
DELETE /api/v1/users/me
GET    /api/v1/users/           # Admin
GET    /api/v1/users/{id}       # Admin
PUT    /api/v1/users/{id}       # Admin
DELETE /api/v1/users/{id}       # Admin
```

### Vendors
```
GET    /api/v1/vendors/
POST   /api/v1/vendors/         # Admin
GET    /api/v1/vendors/dashboard
PUT    /api/v1/vendors/dashboard
GET    /api/v1/vendors/{id}
POST   /api/v1/vendors/{id}/verify  # Admin
```

### Properties, Tours, Vehicles, Boats, Flights
```
GET    /api/v1/{resource}/
POST   /api/v1/{resource}/        # Vendor
GET    /api/v1/{resource}/{id}
PUT    /api/v1/{resource}/{id}    # Owner
DELETE /api/v1/{resource}/{id}    # Owner
POST   /api/v1/{resource}/{id}/restore
```

### Bookings
```
POST /api/v1/bookings/property
POST /api/v1/bookings/tour
GET  /api/v1/bookings/
GET  /api/v1/bookings/{id}
PUT  /api/v1/bookings/{id}/cancel
```

### Search
```
GET /api/v1/search/?q=query&type=properties
GET /api/v1/search/map
```

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose | Version |
|------------|---------|---------|
| **FastAPI** | Web Framework | 0.109.0 |
| **SQLAlchemy** | ORM | 2.0.25 |
| **Pydantic** | Validation | 2.5.3 |
| **PostgreSQL** | Database | 15 |
| **Redis** | Cache/Rate Limit | 7 |
| **Alembic** | Migrations | 1.13.1 |
| **JWT** | Authentication | PyJWT 2.8.0 |
| **Stripe** | Payments | 7.10.0 |

### Frontend
| Technology | Purpose | Version |
|------------|---------|---------|
| **Nuxt.js** | Framework | 3.15.0 |
| **Vue 3** | UI Library | 3.4.15 |
| **TypeScript** | Language | 5.3.3 |
| **Tailwind CSS** | Styling | 3.4.19 |
| **Pinia** | State Management | 2.1.7 |
| **Leaflet** | Maps | 1.9.4 |
| **Chart.js** | Charts | 4.4.1 |

### Infrastructure
| Technology | Purpose |
|------------|---------|
| **Docker** | Containerization |
| **Railway** | Backend Hosting |
| **Vercel** | Frontend Hosting |
| **Cloudinary** | Image CDN |
| **Resend** | Email Service |

---

## 📁 Project Structure

```
costa-rica-travel/
├── 📁 backend/
│   ├── 📁 app/
│   │   ├── 📁 api/v1/endpoints/    # REST controllers
│   │   ├── 📁 core/                 # Config, DB, Security
│   │   ├── 📁 models/               # SQLAlchemy models
│   │   ├── 📁 schemas/              # Pydantic schemas
│   │   ├── 📁 services/             # Business logic
│   │   ├── 📁 middleware/           # Rate limit, auth
│   │   └── 📄 main.py               # Entry point
│   ├── 📁 alembic/versions/         # DB migrations
│   ├── 📄 requirements.txt
│   ├── 📄 Dockerfile
│   └── 📄 railway.toml
│
├── 📁 frontend/
│   ├── 📁 app.vue                   # Root component
│   ├── 📁 pages/                    # Nuxt pages
│   ├── 📁 components/               # Vue components
│   ├── 📁 stores/                   # Pinia stores
│   ├── 📁 composables/              # Vue composables
│   ├── 📁 i18n/                     # Translations
│   ├── 📄 nuxt.config.ts
│   └── 📄 vercel.json
│
├── 📁 docker-compose.yml            # Local development
├── 📄 deploy.sh                     # Deployment script
└── 📄 DEPLOYMENT.md                 # Deployment guide
```

---

## 🚀 Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions.

### Quick Deploy
```bash
# Setup Railway CLI
npm install -g @railway/cli
railway login

# Deploy backend
cd backend
railway up

# Setup Vercel CLI
npm install -g vercel
vercel login

# Deploy frontend
cd frontend
vercel --prod
```

---

## 🔐 Environment Variables

### Backend (.env)
```env
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
STRIPE_SECRET_KEY=sk_live_...
CLOUDINARY_URL=cloudinary://...
RESEND_API_KEY=re_...
```

### Frontend (.env)
```env
NUXT_PUBLIC_API_URL=https://api.costaricatravel.dev
NUXT_PUBLIC_SITE_URL=https://costaricatravel.dev
```

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests (vitest)
cd frontend
npm run test          # Run unit tests
npm run test:coverage # Run with coverage report
```

---

## 📈 Performance

- **API Response Time**: < 100ms average
- **Database**: Connection pooling (20 connections)
- **Caching**: Redis for rate limiting and sessions
- **Images**: Cloudinary with automatic optimization
- **CDN**: Vercel Edge Network

---

## 🌐 Browser Support

- Chrome/Edge (last 2 versions)
- Firefox (last 2 versions)
- Safari (last 2 versions)
- Mobile browsers (iOS Safari, Chrome Android)

---

## 🤝 Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

---

## 📄 License

MIT License © 2024 Costa Rica Travel

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Amazing Python framework
- [Nuxt.js](https://nuxt.com/) - Vue.js made easy
- [Railway](https://railway.app/) - Simple deployment
- [Vercel](https://vercel.com/) - Edge network

---

<p align="center">
  Made with ❤️ in Costa Rica
</p>
