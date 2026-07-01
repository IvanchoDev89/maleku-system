.PHONY: start dev dev-backend dev-frontend stop build build-backend build-frontend test test-backend test-frontend lint lint-backend lint-frontend migrate backup clean pre-commit install

# ─── Development ───────────────────────────────────────────────

start:
	bash start.sh

stop:
	pkill -f "uvicorn app.main:app" 2>/dev/null || true
	pkill -f "node.*nuxt" 2>/dev/null || true
	@echo "Servidores detenidos"

stop-service:
	-systemctl --user stop fastapi-backend.service 2>/dev/null
	-systemctl --user stop nuxt-frontend.service 2>/dev/null
	-systemctl --user stop nuxt-dev-frontend.service 2>/dev/null
	@echo "Servicios detenidos"

dev: dev-backend dev-frontend

dev-backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && npm run dev

dev-backend-service:
	systemd-run --user --unit=fastapi-backend --working-directory=$(PWD)/backend uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend-service:
	systemd-run --user --unit=nuxt-frontend --working-directory=$(PWD)/frontend node node_modules/.bin/nuxi dev

dev-service: dev-backend-service dev-frontend-service

dev-docker:
	docker compose up --build

# ─── Build ─────────────────────────────────────────────────────

build: build-backend build-frontend

build-backend:
	cd backend && docker build -t costarica-backend .

build-frontend:
	cd frontend && npm run build

# ─── Tests ─────────────────────────────────────────────────────

test: test-infra-up test-backend test-frontend test-infra-down

test-reservation:  # smoke test: full reservation flow via live API
	bash backend/tests/test_reservation_flow.sh

test-infra-up:  # Start test DB, Redis, MailHog
	docker-compose -f docker-compose.test.yml up -d

test-infra-down:  # Stop test infrastructure
	docker-compose -f docker-compose.test.yml down

test-infra-reset:  # Stop and remove volumes, then restart
	docker-compose -f docker-compose.test.yml down -v
	docker-compose -f docker-compose.test.yml up -d

test-backend:
	cd backend && python3 -m pytest -v --tb=short -x

test-backend-coverage:
	cd backend && python3 -m pytest -v --tb=short --cov=app --cov-report=term-missing

test-backend-watch:
	cd backend && ptw --now --clear

test-frontend:
	cd frontend && npx vitest run

test-frontend-watch:
	cd frontend && npx vitest

test-frontend-coverage:
	cd frontend && npx vitest run --coverage

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
	rm -rf frontend/.output frontend/node_modules
	rm -rf backend/venv

# ─── Pre-commit ────────────────────────────────────────────────

pre-commit-install:
	pre-commit install

pre-commit-run:
	pre-commit run --all-files
