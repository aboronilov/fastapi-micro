HOST ?= 0.0.0.0	
PORT ?= 8000

# Run application locally
run:
	@echo "Running the application on http://$(HOST):$(PORT)..."
	poetry run uvicorn main:app --host $(HOST) --port $(PORT) --reload --env-file env

# Install/uninstall dependencies
install:
	@echo "Installing dependency $(DEPENDENCY)..."
	poetry add $(DEPENDENCY)

uninstall:
	@echo "Uninstalling dependency $(DEPENDENCY)..."
	poetry remove $(DEPENDENCY)

# Database operations (local)
db-migrate:
	@echo "Creating new migration..."
	@poetry run alembic revision --autogenerate -m "$(MESSAGE)"

db-upgrade:
	@echo "Applying migrations..."
	@poetry run alembic upgrade head

db-seed:
	@echo "Seeding database with sample data..."
	@poetry run python -c "from src.database.seeder import seed_database; from src.database.config import SessionLocal; db = SessionLocal(); seed_database(db); db.close()"

# Docker Compose - Main commands
start: docker-up
	@echo "🚀 All services started! Access the API at http://localhost:8000"

docker-up:
	@echo "Starting all services (FastAPI, PostgreSQL, Redis)..."
	@docker compose up -d
	@echo "✅ Services started successfully"

docker-down:
	@echo "Stopping all services..."
	@docker compose down
	@echo "✅ Services stopped"

docker-build:
	@echo "Building Docker images..."
	@docker compose build
	@echo "✅ Images built successfully"

docker-logs:
	@echo "Showing all service logs..."
	@docker compose logs -f

docker-clean:
	@echo "Cleaning up everything (containers, networks, volumes, images)..."
	@docker compose down -v --rmi all
	@echo "✅ Cleanup completed"

docker-status:
	@echo "Service status:"
	@docker compose ps

# Docker Compose - Utility commands
docker-shell:
	@echo "Opening shell in FastAPI container..."
	@docker compose exec fastapi-app /bin/bash

docker-migrate:
	@echo "Running database migrations..."
	@docker compose exec fastapi-app poetry run alembic upgrade head

docker-seed:
	@echo "Seeding database with sample data..."
	@docker compose exec fastapi-app poetry run python -c "from src.database.seeder import seed_database; from src.database.config import SessionLocal; db = SessionLocal(); seed_database(db); db.close()"

docker-pgadmin:
	@echo "Starting services with pgAdmin..."
	@docker compose --profile tools up -d
	@echo "📊 pgAdmin available at http://localhost:5050"

help:
	@echo "🚀 FastAPI Microservice - Makefile Commands"
	@echo ""
	@echo "📋 Quick Start:"
	@echo "  start        - Start all services (FastAPI + PostgreSQL + Redis)"
	@echo "  docker-up    - Start all services with Docker Compose"
	@echo "  docker-down  - Stop all services"
	@echo "  docker-logs  - View all service logs"
	@echo ""
	@echo "🔧 Development:"
	@echo "  run          - Run application locally (requires local DB)"
	@echo "  install      - Install a dependency (use DEPENDENCY=package)"
	@echo "  uninstall    - Uninstall a dependency (use DEPENDENCY=package)"
	@echo ""
	@echo "🗄️  Database (Local):"
	@echo "  db-migrate   - Create new migration (use MESSAGE='description')"
	@echo "  db-upgrade   - Apply migrations"
	@echo "  db-seed      - Seed database with sample data"
	@echo ""
	@echo "🐳 Docker Commands:"
	@echo "  docker-build - Build Docker images"
	@echo "  docker-clean - Clean everything (containers, networks, volumes, images)"
	@echo "  docker-status- Show service status"
	@echo "  docker-shell - Open shell in FastAPI container"
	@echo "  docker-migrate- Run migrations in container"
	@echo "  docker-seed  - Seed database in container"
	@echo "  docker-pgadmin- Start with pgAdmin (http://localhost:5050)"
	@echo ""
	@echo "💡 Examples:"
	@echo "  make start              # Start everything"
	@echo "  make docker-logs        # View logs"
	@echo "  make db-migrate MESSAGE='add users table'"
	@echo "  make docker-clean       # Clean everything"

.PHONY: run install uninstall db-migrate db-upgrade db-seed start docker-up docker-down docker-build docker-logs docker-clean docker-status docker-shell docker-migrate docker-seed docker-pgadmin help