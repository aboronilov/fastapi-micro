HOST ?= 0.0.0.0	
PORT ?= 8000

# Database configuration
DB_NAME = fastapi_micro_db
DB_USER = postgres
DB_PASSWORD = password
DB_HOST = localhost
DB_PORT = 5432

# Docker configuration
DOCKER_CONTAINER_NAME = fastapi-postgres
DOCKER_IMAGE = postgres:15
DOCKER_VOLUME = fastapi-postgres-data

run:
	@echo "Running the application on http://$(HOST):$(PORT)..."
	poetry run uvicorn main:app --host $(HOST) --port $(PORT) --reload --env-file env

install:
	@echo "Installing dependency $(DEPENDENCY)..."
	poetry add $(DEPENDENCY)

uninstall:
	@echo "Uninstalling dependency $(DEPENDENCY)..."
	poetry remove $(DEPENDENCY)

# Start PostgreSQL in Docker container
db-start:
	@echo "Starting PostgreSQL in Docker container..."
	@docker run -d \
		--name $(DOCKER_CONTAINER_NAME) \
		-e POSTGRES_DB=$(DB_NAME) \
		-e POSTGRES_USER=$(DB_USER) \
		-e POSTGRES_PASSWORD=$(DB_PASSWORD) \
		-p $(DB_PORT):5432 \
		-v $(DOCKER_VOLUME):/var/lib/postgresql/data \
		$(DOCKER_IMAGE) || echo "Container already running or exists"
	@echo "PostgreSQL container started on port $(DB_PORT)"

# Stop PostgreSQL Docker container
db-stop:
	@echo "Stopping PostgreSQL Docker container..."
	@docker stop $(DOCKER_CONTAINER_NAME) || echo "Container not running"
	@echo "PostgreSQL container stopped"

# Remove PostgreSQL Docker container
db-remove:
	@echo "Removing PostgreSQL Docker container..."
	@docker stop $(DOCKER_CONTAINER_NAME) || echo "Container not running"
	@docker rm $(DOCKER_CONTAINER_NAME) || echo "Container not found"
	@echo "PostgreSQL container removed"

# Remove PostgreSQL Docker container and volume
db-clean:
	@echo "Removing PostgreSQL Docker container and volume..."
	@docker stop $(DOCKER_CONTAINER_NAME) || echo "Container not running"
	@docker rm $(DOCKER_CONTAINER_NAME) || echo "Container not found"
	@docker volume rm $(DOCKER_VOLUME) || echo "Volume not found"
	@echo "PostgreSQL container and volume removed"

# Show Docker container status
db-status-docker:
	@echo "Checking Docker container status..."
	@docker ps -a --filter name=$(DOCKER_CONTAINER_NAME) || echo "Docker not available"

# Create PostgreSQL database (for Docker setup)
db-create:
	@echo "Creating PostgreSQL database..."
	@PGPASSWORD=$(DB_PASSWORD) createdb -h $(DB_HOST) -p $(DB_PORT) -U $(DB_USER) $(DB_NAME) || echo "Database already exists"
	@echo "Database '$(DB_NAME)' created successfully!"

# Drop PostgreSQL database
db-drop:
	@echo "Dropping PostgreSQL database..."
	@PGPASSWORD=$(DB_PASSWORD) dropdb -h $(DB_HOST) -p $(DB_PORT) -U $(DB_USER) $(DB_NAME) || echo "Database does not exist"
	@echo "Database '$(DB_NAME)' dropped successfully!"

# Reset database (drop and recreate)
db-reset: db-drop db-create
	@echo "Database reset completed!"

# Show database status
db-status:
	@echo "Checking database connection..."
	@PGPASSWORD=$(DB_PASSWORD) psql -h $(DB_HOST) -p $(DB_PORT) -U $(DB_USER) -d $(DB_NAME) -c "\l" || echo "Database connection failed"

# Complete database setup with Docker
db-setup: db-start
	@echo "Waiting for PostgreSQL to be ready..."
	@sleep 5
	@make db-create
	@echo "Database setup completed!"

# Initialize Alembic
db-init:
	@echo "Initializing Alembic..."
	@poetry run alembic init alembic || echo "Alembic already initialized"

# Create a new migration
db-migrate:
	@echo "Creating new migration..."
	@poetry run alembic revision --autogenerate -m "$(MESSAGE)"

# Apply migrations
db-upgrade:
	@echo "Applying migrations..."
	@poetry run alembic upgrade head

# Rollback migrations
db-downgrade:
	@echo "Rolling back migrations..."
	@poetry run alembic downgrade -1

# Show migration history
db-history:
	@echo "Migration history:"
	@poetry run alembic history

# Show current migration
db-current:
	@echo "Current migration:"
	@poetry run alembic current

# Complete database setup with migrations
db-setup-complete: db-setup db-init db-upgrade
	@echo "Complete database setup with migrations finished!"

# Create initial migration
db-migrate-init:
	@echo "Creating initial migration..."
	@mkdir -p alembic/versions
	@poetry run alembic revision --autogenerate -m "Initial migration"

# Create a new migration with message
db-migrate-create:
	@echo "Creating new migration..."
	@if [ -z "$(MESSAGE)" ]; then \
		echo "Error: MESSAGE is required. Use: make db-migrate-create MESSAGE='description'"; \
		exit 1; \
	fi
	@poetry run alembic revision --autogenerate -m "$(MESSAGE)"

# Complete database setup with initial migration
db-setup-complete: db-setup db-init db-migrate-init db-upgrade
	@echo "Complete database setup with initial migration finished!"

# Seed database with sample data
db-seed:
	@echo "Seeding database with sample data..."
	@poetry run python -c "from src.database.seeder import seed_database; from src.database.config import SessionLocal; db = SessionLocal(); seed_database(db); db.close()"

# Complete setup with seeding
db-setup-full: db-setup-complete db-seed
	@echo "Complete database setup with sample data finished!"

# Docker Compose commands
docker-up:
	@echo "Starting FastAPI microservice with Docker Compose..."
	@docker compose up -d
	@echo "Services started! Access the API at http://localhost:8000"

docker-down:
	@echo "Stopping Docker Compose services..."
	@docker compose down
	@echo "Services stopped"

docker-build:
	@echo "Building Docker images..."
	@docker compose build
	@echo "Images built successfully"

docker-rebuild:
	@echo "Rebuilding Docker images (no cache)..."
	@docker compose build --no-cache
	@echo "Images rebuilt successfully"

docker-logs:
	@echo "Showing Docker Compose logs..."
	@docker compose logs -f

docker-logs-app:
	@echo "Showing FastAPI application logs..."
	@docker compose logs -f fastapi-app

docker-logs-db:
	@echo "Showing PostgreSQL database logs..."
	@docker compose logs -f postgres

docker-logs-redis:
	@echo "Showing Redis logs..."
	@docker compose logs -f redis

docker-restart:
	@echo "Restarting Docker Compose services..."
	@docker compose restart
	@echo "Services restarted"

docker-restart-app:
	@echo "Restarting FastAPI application..."
	@docker compose restart fastapi-app
	@echo "Application restarted"

docker-clean:
	@echo "Cleaning up Docker Compose (containers, networks, volumes)..."
	@docker compose down -v --rmi all
	@echo "Cleanup completed"

docker-clean-volumes:
	@echo "Removing Docker Compose volumes..."
	@docker compose down -v
	@echo "Volumes removed"

docker-status:
	@echo "Docker Compose service status:"
	@docker compose ps

docker-exec-app:
	@echo "Executing command in FastAPI container..."
	@docker compose exec fastapi-app $(CMD)

docker-migrate:
	@echo "Running database migrations in container..."
	@docker compose exec fastapi-app poetry run alembic upgrade head

docker-seed:
	@echo "Seeding database in container..."
	@docker compose exec fastapi-app poetry run python -c "from src.database.seeder import seed_database; from src.database.config import SessionLocal; db = SessionLocal(); seed_database(db); db.close()"

docker-shell:
	@echo "Opening shell in FastAPI container..."
	@docker compose exec fastapi-app /bin/bash

docker-redis-cli:
	@echo "Opening Redis CLI..."
	@docker compose exec redis redis-cli

docker-redis-ping:
	@echo "Testing Redis connection..."
	@docker compose exec redis redis-cli ping

docker-pgadmin:
	@echo "Starting services with pgAdmin..."
	@docker compose --profile tools up -d
	@echo "pgAdmin available at http://localhost:5050"

help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "Application:"
	@echo "  run - Run the application locally"
	@echo "  install - Install a dependency"
	@echo "  uninstall - Uninstall a dependency"
	@echo ""
	@echo "Docker Compose:"
	@echo "  docker-up - Start FastAPI microservice with Docker Compose"
	@echo "  docker-down - Stop Docker Compose services"
	@echo "  docker-build - Build Docker images"
	@echo "  docker-rebuild - Rebuild Docker images (no cache)"
	@echo "  docker-logs - Show all Docker Compose logs"
	@echo "  docker-logs-app - Show FastAPI application logs"
	@echo "  docker-logs-db - Show PostgreSQL database logs"
	@echo "  docker-logs-redis - Show Redis logs"
	@echo "  docker-restart - Restart all Docker Compose services"
	@echo "  docker-restart-app - Restart FastAPI application only"
	@echo "  docker-clean - Clean up Docker Compose (containers, networks, volumes, images)"
	@echo "  docker-clean-volumes - Remove Docker Compose volumes"
	@echo "  docker-status - Show Docker Compose service status"
	@echo "  docker-exec-app - Execute command in FastAPI container (use CMD='command')"
	@echo "  docker-migrate - Run database migrations in container"
	@echo "  docker-seed - Seed database in container"
	@echo "  docker-shell - Open shell in FastAPI container"
	@echo "  docker-redis-cli - Open Redis CLI"
	@echo "  docker-redis-ping - Test Redis connection"
	@echo "  docker-pgadmin - Start services with pgAdmin"
	@echo ""
	@echo "Database (Local):"
	@echo "  db-setup - Complete database setup with Docker"
	@echo "  db-start - Start PostgreSQL in Docker container"
	@echo "  db-stop - Stop PostgreSQL Docker container"
	@echo "  db-remove - Remove PostgreSQL Docker container"
	@echo "  db-clean - Remove PostgreSQL Docker container and volume"
	@echo "  db-status-docker - Check Docker container status"
	@echo "  db-create - Create PostgreSQL database"
	@echo "  db-drop - Drop PostgreSQL database"
	@echo "  db-reset - Reset database (drop and recreate)"
	@echo "  db-status - Check database status"
	@echo "  db-init - Initialize Alembic"
	@echo "  db-migrate - Create a new migration"
	@echo "  db-upgrade - Apply migrations"
	@echo "  db-downgrade - Rollback migrations"
	@echo "  db-history - Show migration history"
	@echo "  db-current - Show current migration"
	@echo "  db-setup-complete - Complete database setup with migrations"
	@echo "  db-setup-full - Complete database setup with sample data"
	@echo "  db-seed - Seed database with sample data"
	@echo ""
	@echo "Examples:"
	@echo "  make docker-up          # Start the microservice"
	@echo "  make docker-logs-app    # View application logs"
	@echo "  make docker-exec-app CMD='poetry run alembic current'  # Run command in container"
	@echo "  make docker-clean       # Clean everything"

.PHONY: run install uninstall db-setup db-start db-stop db-remove db-clean db-status-docker db-create db-drop db-reset db-status help db-init db-migrate db-upgrade db-downgrade db-history db-current db-setup-complete db-setup-full db-seed docker-up docker-down docker-build docker-rebuild docker-logs docker-logs-app docker-logs-db docker-logs-redis docker-restart docker-restart-app docker-clean docker-clean-volumes docker-status docker-exec-app docker-migrate docker-seed docker-shell docker-redis-cli docker-redis-ping docker-pgadmin