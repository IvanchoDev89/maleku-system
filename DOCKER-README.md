# 🐳 Docker Development Setup

## Quick Start

```bash
# Build and start all services
docker compose up --build

# Or detached mode (background)
docker compose up --build -d
```

## Services

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | Nuxt.js app |
| Backend API | http://localhost:8000 | FastAPI |
| API Docs | http://localhost:8000/docs | Swagger UI |
| PostgreSQL | localhost:5434 | Database |
| Redis | localhost:6379 | Cache |

## Commands

```bash
# Stop all services
docker compose down

# View logs
docker compose logs -f

# View specific service logs
docker compose logs -f backend
docker compose logs -f frontend

# Restart a service
docker compose restart backend
docker compose restart frontend

# Shell into backend
docker compose exec backend bash

# Shell into frontend
docker compose exec frontend sh

# Rebuild everything
docker compose down
docker compose up --build
```

## Development

- Backend code changes are automatically reloaded (hot reload)
- Frontend code changes are automatically reloaded (Nuxt dev mode)
- Database persists between restarts

## Troubleshooting

### Port already in use
```bash
# Kill any existing processes on ports 3000, 8000, 5432, 6379
sudo lsof -ti:3000 | xargs kill -9
sudo lsof -ti:8000 | xargs kill -9
```

### Clean restart
```bash
docker compose down -v  # Remove volumes too
docker compose up --build
```
