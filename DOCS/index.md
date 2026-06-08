# Costa Rica Travel — Documentación

Bienvenido a la documentación oficial de Costa Rica Travel, una plataforma de turismo multi-vendor.

## Índice

| Documento | Descripción |
|-----------|-------------|
| [API Reference](../API.md) | Documentación completa de endpoints REST, schemas, autenticación y ejemplos |
| [Arquitectura](../ARCHITECTURE.md) | Stack tecnológico, estructura del proyecto y diseño del sistema |
| [Deploy](../DEPLOYMENT.md) | Guía de deploy en Railway (backend) y Vercel (frontend) |
| [Contribución](../CONTRIBUTING.md) | Guía para contribuir al proyecto |
| [README Principal](../README.md) | Overview del proyecto, features y quick start |

## Stack

| Capa | Tecnología |
|------|-----------|
| Frontend | Nuxt.js 3, Tailwind CSS, Pinia, i18n |
| Backend | FastAPI, SQLAlchemy 2.0 async, Pydantic |
| Base de datos | PostgreSQL 16 (GIN, tsvector, advisory locks) |
| Cache | Redis (rate limiting, caché, sesiones) |
| Imágenes | Cloudinary (CDN, transformaciones) |
| Pagos | Stripe (Checkout, Connect, webhooks) |
| Email | MailHog (dev), Resend (prod) |
| Monitoreo | Sentry (errores), Prometheus (métricas) |

## Enlaces Rápidos

- **API Docs (Swagger):** `http://localhost:8000/docs`
- **API Docs (ReDoc):** `http://localhost:8000/redoc`
- **Frontend:** `http://localhost:3000`
- **MailHog:** `http://localhost:8025`
- **Métricas:** `http://localhost:8000/metrics`
