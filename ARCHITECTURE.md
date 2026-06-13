# Arquitectura del Sistema - Costa Rica Travel

Documentación técnica detallada de la arquitectura del sistema.

## 📐 Visión General

Costa Rica Travel es una aplicación full-stack con arquitectura de microservicios ligeros, diseñada para escalabilidad horizontal y alta disponibilidad.

### Stack Arquitectónico

```
┌─────────────────────────────────────────────────────────────┐
│                         PRESENTATION                        │
├─────────────────────────────────────────────────────────────┤
│  Nuxt.js 3 (Vue 3 + TypeScript)                             │
│  ├── SSR/SSG para SEO                                       │
│  ├── i18n (ES/EN/FR)                                        │
│  ├── Tailwind CSS                                           │
│  ├── Pinia State Management                                 │
│  └── Leaflet Maps                                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS / REST API
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                         API GATEWAY                           │
├─────────────────────────────────────────────────────────────┤
│  FastAPI                                                    │
│  ├── JWT Authentication                                     │
│  ├── Rate Limiting (60 req/min)                             │
│  ├── CORS Middleware                                        │
│  ├── Request Validation (Pydantic)                          │
│  └── OpenAPI / Swagger Docs                                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ Business Logic
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        SERVICE LAYER                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │   Auth      │  │   Search    │  │  Booking    │       │
│  │   Service   │  │   Service   │  │  Service    │       │
│  └─────────────┘  └─────────────┘  └─────────────┘       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │   Vendor    │  │  Property   │  │  Payment    │       │
│  │   Service   │  │   Service   │  │  Service    │       │
│  └─────────────┘  └─────────────┘  └─────────────┘       │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ Data Access
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      DATA LAYER                             │
├─────────────────────────────────────────────────────────────┤
│  SQLAlchemy 2.0 (Async)                                     │
│  ├── Connection Pooling                                     │
│  ├── Transaction Management                                 │
│  └── Repository Pattern                                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ Storage
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      INFRASTRUCTURE                         │
├───────────────┬───────────────┬─────────────────────────────┤
│ PostgreSQL    │ Redis         │ Cloudinary                   │
│ (Primary DB)  │ (Cache/Queue) │ (Media Storage)            │
├───────────────┼───────────────┼─────────────────────────────┤
│ • GIN Indexes │ • Sessions    │ • Image Optimization        │
│ • Full-text   │ • Rate Limit  │ • CDN Delivery              │
│ • JSONB       │ • Cache       │ • Transformations           │
│ • Soft Delete │ • Pub/Sub     │                             │
└───────────────┴───────────────┴─────────────────────────────┘
```

---

## 🏗️ Componentes del Sistema

### 1. Frontend (Nuxt.js)

#### Estructura de Carpetas
```
frontend/
├── app.vue                    # Application wrapper
├── pages/                     # File-based routing
│   ├── index.vue             # Home
│   ├── properties/
│   │   ├── index.vue         # Property list
│   │   └── [id].vue          # Property detail
│   ├── tours/
│   ├── vehicles/
│   ├── boats/
│   ├── flights/
│   ├── auth/
│   │   ├── login.vue
│   │   ├── register.vue
│   │   └── forgot-password.vue
│   ├── vendor/
│   │   └── dashboard.vue
│   └── admin/
│       └── ...
├── components/
│   ├── ui/                   # Base components
│   ├── forms/                # Form components
│   └── search/               # Search components
├── stores/                    # Pinia stores
│   ├── auth.ts
│   ├── properties.ts
│   └── search.ts
├── composables/               # Vue composables
│   ├── useAuth.ts
│   ├── useApi.ts
│   └── useSearch.ts
├── middleware/                # Route middleware
│   ├── auth.ts
│   └── admin.ts
├── i18n/                      # Translations
│   ├── es.json
│   ├── en.json
│   └── fr.json
└── types/                     # TypeScript types
    └── index.ts
```

#### Patrones de Diseño
- **Composition API**: Todos los componentes usan `<script setup>`
- **Composables**: Lógica reutilizable extraída (useAuth, useApi, etc.)
- **Pinia Stores**: Estado centralizado con acciones asíncronas
- **Middleware**: Protección de rutas (auth, admin, vendor)

---

### 2. Backend (FastAPI)

#### Estructura de Capas

```
Request
   │
   ▼
┌─────────────────────────────────────┐
│  MIDDLEWARE (Process Order)         │
│  1. ErrorHandlerMiddleware           │
│  2. CORSMiddleware                   │
│  3. RateLimitMiddleware (60/min)    │
│  4. SlowAPIMiddleware                │
└─────────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────────┐
│  ROUTER (api/v1/endpoints/)          │
│  - Input Validation (Pydantic)       │
│  - Dependency Injection              │
│  - Role-based Access Control         │
└─────────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────────┐
│  SERVICE LAYER (services/)          │
│  - Business Logic                    │
│  - External API Integration          │
│  - Transaction Coordination          │
└─────────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────────┐
│  REPOSITORY (models/ + implicit)      │
│  - SQLAlchemy ORM                    │
│  - Query Building                    │
│  - Soft Delete Logic                 │
└─────────────────────────────────────┘
   │
   ▼
Database / Redis / External APIs
```

#### Módulos Principales

| Módulo | Descripción | Endpoints |
|--------|-------------|-----------|
| **Auth** | Autenticación JWT, refresh tokens, email verification | 8 |
| **Users** | Gestión de usuarios, perfiles, admin CRUD | 7 |
| **Vendors** | Registro de vendors, dashboard, verificación | 8 |
| **Properties** | Hoteles, casas, villas | 7 |
| **Tours** | Tours y actividades | 7 |
| **Vehicles** | Alquiler de vehículos | 7 |
| **Boats** | Alquiler de botes | 7 |
| **Flights** | Vuelos internos | 7 |
| **Transport** | Traslados | 7 |
| **Bookings** | Sistema de reservas | 5 |
| **Reviews** | Ratings y comentarios | 6 |
| **Blog** | CMS de contenido | 8 |
| **Chat** | Mensajería | 4 |
| **Search** | Búsqueda full-text | 4 |

---

## 📊 Modelo de Datos

### Diagrama ER (Entidad-Relación)

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│    User     │       │   Vendor    │       │  Property   │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ id (PK)     │◄──────┤ id (PK)     │◄──────┤ id (PK)     │
│ email       │       │ user_id(FK) │       │ vendor_id   │
│ password    │       │ company_name│       │ name        │
│ role        │       │ is_verified │       │ location    │
│ is_active   │       │ commission  │       │ price       │
│ created_at  │       │ created_at  │       │ features[]  │
└─────────────┘       └─────────────┘       └─────────────┘
        │                     │                     │
        │                     │                     │
        ▼                     ▼                     ▼
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│   Booking   │       │    Tour     │       │   Review    │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ id (PK)     │       │ id (PK)     │       │ id (PK)     │
│ user_id(FK) │       │ vendor_id   │       │ user_id(FK) │
│ property_id │       │ title       │       │ property_id │
│ status      │       │ description │       │ rating      │
│ dates       │       │ price       │       │ comment     │
│ total       │       │ duration    │       │ created_at  │
└─────────────┘       └─────────────┘       └─────────────┘
```

### Modelos Core

#### User Model
```python
class User(Base):
    id: int (PK)
    email: str (unique, indexed)
    password_hash: str
    role: Enum[SUPER_ADMIN, ADMIN, VENDOR, CLIENT]
    is_active: bool
    is_verified: bool
    email_verification_token: str
    password_reset_token: str
    failed_login_attempts: int
    locked_until: datetime
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime (soft delete)
```

#### Vendor Model
```python
class Vendor(Base):
    id: int (PK)
    user_id: int (FK → User)
    company_name: str
    slug: str (unique, indexed)
    description: str
    logo_url: str
    commission_rate: float (default 0.10)
    is_verified: bool
    is_active: bool
    verification_documents: JSONB
    # Relaciones
    properties: List[Property]
    tours: List[Tour]
    vehicles: List[Vehicle]
```

#### Property Model (Polymorphic Pattern)
```python
class Property(Base):
    id: int (PK)
    vendor_id: int (FK → Vendor)
    name: str
    slug: str (unique)
    description: str
    property_type: Enum[HOTEL, VILLA, CABIN, HOSTEL]
    location: JSONB {lat, lng, address, city, region}
    price_per_night: Decimal
    currency: str (default 'USD')
    max_guests: int
    bedrooms: int
    bathrooms: int
    amenities: JSONB[]
    images: JSONB[]
    availability_calendar: JSONB
    # Search
    search_vector: TSVector (GIN index)
    # Audit
    created_at, updated_at, deleted_at
```

---

## 🔐 Seguridad

### Autenticación & Autorización

```
┌─────────────────────────────────────────┐
│           AUTH FLOW                     │
├─────────────────────────────────────────┤
│                                         │
│  1. Login (email/password)              │
│     ↓                                   │
│  2. Validate Credentials                │
│     ↓                                   │
│  3. Generate Tokens                     │
│     ├── Access Token (15 min, JWT)      │
│     └── Refresh Token (7 days, JWT)     │
│     ↓                                   │
│  4. Return to Client                    │
│     ↓                                   │
│  5. Client stores:                      │
│     ├── Access: memory (Pinia)          │
│     └── Refresh: httpOnly cookie        │
│     ↓                                   │
│  6. Subsequent Requests                 │
│     └── Authorization: Bearer <token>   │
│                                         │
└─────────────────────────────────────────┘
```

### Rate Limiting

```python
# 60 requests per minute per IP
@app.middleware("http")
async def rate_limit(request: Request, call_next):
    client_ip = request.client.host
    key = f"rate_limit:{client_ip}"

    current = await redis.incr(key)
    if current == 1:
        await redis.expire(key, 60)

    if current > 60:
        raise HTTPException(429, "Too many requests")

    return await call_next(request)
```

### Password Security
- **Hashing**: bcrypt with salt rounds 12
- **Validation**: Min 8 chars, uppercase, lowercase, digit, special char
- **Reset Flow**: 1-hour expiration tokens via email
- **Lockout**: 5 failed attempts = 15 min lock

---

## 🔍 Búsqueda (Full-Text)

### Implementación PostgreSQL

```sql
-- GIN Index para búsqueda rápida
CREATE INDEX idx_properties_search ON properties
USING GIN(search_vector);

-- Trigger para actualizar search_vector
CREATE OR REPLACE FUNCTION update_search_vector()
RETURNS TRIGGER AS $$
BEGIN
  NEW.search_vector :=
    setweight(to_tsvector('spanish', COALESCE(NEW.name, '')), 'A') ||
    setweight(to_tsvector('spanish', COALESCE(NEW.description, '')), 'B') ||
    setweight(to_tsvector('spanish', COALESCE(NEW.location->>'city', '')), 'C');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

### API de Búsqueda
```python
GET /api/v1/search?q=playa&location=manuel%20antonio&type=properties

Response:
{
  "results": [...],
  "total": 42,
  "page": 1,
  "page_size": 20
}
```

---

## 💳 Pagos (Stripe)

### Flujo de Pago

```
1. User selects dates/property
   ↓
2. Check availability (API)
   ↓
3. Create Booking (status: PENDING)
   ↓
4. Create Stripe Checkout Session
   ↓
5. Redirect user to Stripe
   ↓
6. User completes payment
   ↓
7. Stripe webhook → Backend
   ↓
8. Update Booking (status: CONFIRMED)
   ↓
9. Send confirmation email
   ↓
10. Commission calculated (10%)
```

### Modelo de Comisiones
```python
# Configurable per vendor
vendor_commission = vendor.commission_rate  # default 0.10

# On successful payment
platform_fee = total_amount * vendor_commission
vendor_payout = total_amount - platform_fee

# Stripe Connect for automatic payout
# Or manual payout via admin panel
```

---

## 📦 Despliegue

### Arquitectura de Producción

```
┌─────────────────────────────────────────────────────────────┐
│                         USERS                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Cloudflare DNS + CDN                                       │
│  - SSL Termination                                          │
│  - DDoS Protection                                          │
│  - Caching                                                  │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
              ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────────┐
│  Vercel (Frontend)      │     │  Railway (Backend)          │
│  - Edge Network           │     │  - Docker Containers        │
│  - SSR/SSG               │     │  - Auto-scaling             │
│  - i18n Routing          │     │  - Health Checks            │
│  - 99.99% Uptime         │     │  - Zero-downtime Deploy     │
└─────────────────────────┘     └─────────────────────────────┘
                                              │
                    ┌─────────────────────────┼─────────────────────────┐
                    │                         │                         │
                    ▼                         ▼                         ▼
┌─────────────────────────┐ ┌─────────────────────────┐ ┌─────────────┐
│  Railway PostgreSQL     │ │  Railway Redis          │ │  Cloudinary │
│  - Automatic Backups    │ │  - Session Store        │ │  - Images   │
│  - Point-in-time        │ │  - Rate Limiting        │ │  - CDN      │
│    Recovery             │ │  - Caching              │ │             │
└─────────────────────────┘ └─────────────────────────┘ └─────────────┘
```

---

## 📈 Escalabilidad

### Horizontal Scaling
```
┌─────────────────────────────────────────┐
│  Load Balancer (Railway/Vercel)        │
└─────────────────────────────────────────┘
                    │
    ┌───────────────┼───────────────┐
    │               │               │
    ▼               ▼               ▼
┌─────────┐   ┌─────────┐   ┌─────────┐
│ API 1   │   │ API 2   │   │ API 3   │
│ (FastAPI)│   │ (FastAPI)│   │ (FastAPI)│
└─────────┘   └─────────┘   └─────────┘
    │               │               │
    └───────────────┼───────────────┘
                    │
                    ▼
            ┌───────────────┐
            │  PostgreSQL   │
            │   Primary     │
            └───────────────┘
                    │
                    ▼
            ┌───────────────┐
            │  PostgreSQL   │
            │   Read Replica│
            └───────────────┘
```

### Caching Strategy
```
Level 1: Browser Cache (static assets, images)
Level 2: CDN Cache (Vercel Edge, Cloudinary)
Level 3: Application Cache (Redis for sessions)
Level 4: Database Cache (PostgreSQL shared_buffers)
```

---

## 🧪 Testing Strategy

### Pirámide de Testing
```
         /
        /  \     E2E Tests (Playwright)
       /    \    └── Critical user journeys
      /──────\
     /        \  Integration Tests
    /          \ └── API endpoints, DB queries
   /────────────\
  /              \ Unit Tests
 /                \└── Services, utilities
/──────────────────\
```

### Cobertura Mínima
- Unit Tests: 70%
- Integration Tests: 50%
- E2E Tests: 10 critical paths

---

## 📚 Recursos Adicionales

- [API Documentation](./API.md)
- [Contributing Guide](./CONTRIBUTING.md)
- [Deployment Guide](./DEPLOYMENT.md)
- [Security Policy](./SECURITY.md)

---

<p align="center">
  <strong>Arquitectura Version 1.0</strong><br>
  Last Updated: May 2024
</p>
