.PHONY: dev dev-backend dev-frontend build build-backend build-frontend test test-backend test-frontend lint lint-backend lint-frontend migrate backup clean pre-commit install

# ─── Development ───────────────────────────────────────────────

dev: dev-backend dev-frontend

dev-backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && npm run dev

dev-docker:
	docker compose up --build

# ─── Build ─────────────────────────────────────────────────────

build: build-backend build-frontend

build-backend:
	cd backend && docker build -t costarica-backend .

build-frontend:
	cd frontend && npm run build

# ─── Tests ─────────────────────────────────────────────────────

test: test-backend test-frontend

test-backend:
	cd backend && python -m pytest -v --tb=short -x

test-backend-coverage:
	cd backend && python -m pytest -v --tb=short --cov=app --cov-report=term-missing

test-frontend:
	cd frontend && npx vitest run

test-frontend-watch:
	cd frontend && npx vitest

test-e2e:
	npx playwright test

# ─── Lint ──────────────────────────────────────────────────────

lint: lint-backend lint-frontend

lint-backend:
	ruff check backend/ && ruff format --check backend/

lint-backend-fix:
	ruff check --fix backend/ && ruff format backend/

lint-frontend:
	cd frontend && npx eslint . --ext .vue,.js,.ts

# ─── Security ──────────────────────────────────────────────────

security:
	bandit -r backend/ -x backend/tests,backend/venv,backend/.venv
	cd frontend && npm audit

# ─── Database ──────────────────────────────────────────────────

migrate:
	cd backend && alembic upgrade head

migration:
	cd backend && alembic revision --autogenerate -m "$(message)"

migration-create:
	cd backend && alembic revision -m "$(message)"

# ─── Backup ────────────────────────────────────────────────────

backup:
	./scripts/backup-db.sh

backup-local:
	./scripts/backup-db.sh ./backups

# ─── Docker ────────────────────────────────────────────────────

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

docker-staging:
	docker compose -f docker-compose.staging.yml up -d --build

# ─── Clean ─────────────────────────────────────────────────────

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf frontend/.nuxt frontend/.output frontend/node_modules
	rm -rf backend/venv

# ─── Pre-commit ────────────────────────────────────────────────

pre-commit-install:
	pre-commit install

pre-commit-run:
	pre-commit run --all-files
