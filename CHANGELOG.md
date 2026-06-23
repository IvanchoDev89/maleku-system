# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Fixed
- Tours endpoint query params: `q`, `destination`, `min_duration`, `max_duration`, `sort`, `min_rating` now work correctly
- Missing enum values (`BEACH`, `WILDLIFE`, `CULTURE`, `MEDIUM`, `HARD`) in backend models to prevent 500 errors
- `v-if`/`v-for` conflict on `SearchFilters.vue`
- Active filter tags now show translated labels
- Duplicate `tours` sections in locale JSON files causing decode errors

### Added
- Mobile filter drawer in `SearchFilters.vue` with slide-in animation
- Translation for all filter option labels in `useSearch.ts`

## [1.0.0] - 2025

### Fixed
- Redirect clients to `/` instead of `/dashboard` after login
- Backend session concurrency, missing columns, search route
- AuditService `entity_id` and serialization bugs
- Contact endpoint, vendor documents, i18n fallbacks
- Console errors and superadmin access crash
- Duplicate split-screen layout on login pages
- SQLAlchemy + Redis + async bugs
- Pagination params unification across all endpoints
- Trailing slash redirect (`redirect_slashes=False`)

### Added
- Integration tests, monitoring, feature flags, rate limiting, e2e tests
- SSR, PWA support, Pinia stores, background tasks
- Trip Planner API (`/trip_planner/plans`)
- Superadmin endpoints (users, vendors, bookings, tours, audit, content)
- 10 pagination unit tests + formatNumber edge case tests
- Pre-commit hooks, CI pipeline (Redis, ruff, vitest, deploy)
- Swagger summaries, descriptions, and tags on 52 endpoints
- Parallel queries for landing, search, and upload
- GZip compression, cache fixes, structured logging, Prometheus metrics
- i18n completions (46 keys), error toasts, hybrid dev mode
- Security: runtime bcrypt rounds, SLOWAPI rate limiting, real CSV export, migration 006
- End-to-end local dev setup (hybrid Docker + native)

### Changed
- Migrated `nuxt-icon` v1 → `@nuxt/icon` v1
- Centralized pagination with `paginate_flat()` across 7 endpoints
- `docker-compose` → `docker compose` (Compose V2)
- Auth deduplication and cleanup

### Docs
- Created `DOCS/` hub, `ARCHITECTURE.md`, `CHANGELOG.md`, `SECURITY.md`, `LICENSE`
- Updated all endpoint docs in `API.md` with query params, request/response schemas
- Updated `README.md` with project structure, deployment guide, API table

## [0.1.0] - 2024

### Added
- Initial monorepo with FastAPI backend + Nuxt 3 frontend
- PostgreSQL database with Alembic migrations
- JWT authentication with refresh tokens
- Multi-vendor marketplace (properties, tours, vehicles, boats, flights)
- Booking engine with availability calendar
- Full-text search with PostgreSQL tsvector
- Multi-language support (ES, EN, FR)
- Tailwind CSS responsive design
- Docker Compose development environment
- Stripe payment integration
- Blog CMS and marketing automation
