# FastAPI Microservices Makefile

.PHONY: help install dev test lint format clean docker-build docker-up docker-down docker-logs docker-shell migrate migrate-reset db-reset kafka-test event-test health-check gateway-test services-test all-services-test

# Default target
help:
	@echo "FastAPI Microservices - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  install        - Install dependencies"
	@echo "  dev            - Start development server"
	@echo "  test           - Run all tests"
	@echo "  test-unit      - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-coverage  - Run tests with coverage report"
	@echo "  test-user      - Run user service tests"
	@echo "  test-task      - Run task service tests"
	@echo "  test-notification - Run notification service tests"
	@echo "  test-shared    - Run shared component tests"
	@echo "  lint           - Run linting"
	@echo "  format         - Format code"
	@echo "  clean          - Clean cache and temporary files"
	@echo ""
	@echo "Docker & Microservices:"
	@echo "  docker-build   - Build all Docker images"
	@echo "  docker-up      - Start all services (microservices + infrastructure)"
	@echo "  docker-down    - Stop all services"
	@echo "  docker-logs    - Show logs for all services"
	@echo "  docker-shell   - Open shell in API Gateway container"
	@echo ""
	@echo "Database:"
	@echo "  migrate        - Run database migrations"
	@echo "  migrate-reset  - Reset and run migrations"
	@echo "  db-reset       - Reset database completely"
	@echo ""
	@echo "Testing & Health Checks:"
	@echo "  kafka-test     - Test Kafka event bus"
	@echo "  event-test     - Test event publishing"
	@echo "  health-check   - Check health of all services"
	@echo "  gateway-test   - Test API Gateway functionality"
	@echo "  services-test  - Test individual microservices"
	@echo "  all-services-test - Test complete microservices workflow"
	@echo ""
	@echo "Individual Services:"
	@echo "  start-gateway  - Start only API Gateway"
	@echo "  start-user     - Start only User Service"
	@echo "  start-task     - Start only Task Service"
	@echo "  start-notification - Start only Notification Service"
	@echo "  start-infra    - Start only infrastructure (DB, Redis, Kafka)"

# Development commands
install:
	@echo "Installing dependencies..."
	poetry install

dev:
	@echo "Starting development server..."
	poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload

test:
	@echo "Running all tests..."
	poetry run pytest

test-unit:
	@echo "Running unit tests..."
	poetry run pytest -m unit

test-integration:
	@echo "Running integration tests..."
	poetry run pytest -m integration

test-coverage:
	@echo "Running tests with coverage..."
	poetry run pytest --cov=src --cov-report=html --cov-report=term-missing

test-user:
	@echo "Running user service tests..."
	poetry run pytest tests/unit/services/user/ tests/integration/test_user_service_api.py

test-task:
	@echo "Running task service tests..."
	poetry run pytest tests/unit/services/task/ tests/integration/test_task_service_api.py

test-notification:
	@echo "Running notification service tests..."
	poetry run pytest tests/unit/services/notification/ tests/integration/test_notification_service_api.py

test-shared:
	@echo "Running shared component tests..."
	poetry run pytest tests/unit/shared/

lint:
	@echo "Running linting..."
	poetry run pyright src/
	poetry run flake8 src/

format:
	@echo "Formatting code..."
	poetry run black src/
	poetry run isort src/

clean:
	@echo "Cleaning cache and temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf .coverage

# Docker commands
docker-build:
	@echo "Building Docker images..."
	docker compose build

docker-up:
	@echo "Starting all services..."
	docker compose up -d

docker-down:
	@echo "Stopping all services..."
	docker compose down

docker-logs:
	@echo "Showing logs for all services..."
	docker compose logs -f

docker-shell:
	@echo "Opening shell in API Gateway container..."
	docker compose exec api-gateway /bin/bash

# Database commands
migrate:
	@echo "Running database migrations..."
	docker compose exec fastapi-app poetry run alembic upgrade head

migrate-reset:
	@echo "Resetting and running migrations..."
	docker compose exec fastapi-app poetry run alembic downgrade base
	docker compose exec fastapi-app poetry run alembic upgrade head

db-reset:
	@echo "Resetting database completely..."
	docker compose down -v
	docker compose up -d postgres
	sleep 10
	docker compose exec postgres psql -U postgres -d fastapi_micro_db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
	docker compose exec fastapi-app poetry run alembic upgrade head

# Testing commands
kafka-test:
	@echo "Testing Kafka event bus..."
	poetry run python test_events.py

kafka-fixes-test:
	@echo "Testing Kafka client fixes..."
	poetry run python test_kafka_fixes.py

event-test:
	@echo "Testing event publishing..."
	poetry run python test_events.py

health-check:
	@echo "Checking health of all services..."
	@echo "API Gateway:"
	@curl -s http://localhost:8000/health | jq . || echo "❌ API Gateway not responding"
	@echo ""
	@echo "User Service:"
	@curl -s http://localhost:8001/health | jq . || echo "❌ User Service not responding"
	@echo ""
	@echo "Task Service:"
	@curl -s http://localhost:8002/health | jq . || echo "❌ Task Service not responding"
	@echo ""
	@echo "Notification Service:"
	@curl -s http://localhost:8003/health | jq . || echo "❌ Notification Service not responding"
	@echo ""
	@echo "Legacy App:"
	@curl -s http://localhost:8004/health/db | jq . || echo "❌ Legacy App not responding"

gateway-test:
	@echo "Testing API Gateway functionality..."
	@echo "Testing service discovery:"
	@curl -s http://localhost:8000/services | jq .
	@echo ""
	@echo "Testing routing to user service:"
	@curl -s http://localhost:8000/users | jq . || echo "❌ User service routing failed"
	@echo ""
	@echo "Testing routing to task service:"
	@curl -s http://localhost:8000/tasks | jq . || echo "❌ Task service routing failed"
	@echo ""
	@echo "Testing routing to notification service:"
	@curl -s http://localhost:8000/notifications | jq . || echo "❌ Notification service routing failed"

services-test:
	@echo "Testing individual microservices..."
	@echo "User Service API:"
	@curl -s http://localhost:8001/docs || echo "❌ User Service docs not available"
	@echo ""
	@echo "Task Service API:"
	@curl -s http://localhost:8002/docs || echo "❌ Task Service docs not available"
	@echo ""
	@echo "Notification Service API:"
	@curl -s http://localhost:8003/docs || echo "❌ Notification Service docs not available"

all-services-test:
	@echo "Testing complete microservices workflow..."
	@echo "1. Creating user through API Gateway..."
	@USER_RESPONSE=$$(curl -s -X POST http://localhost:8000/users \
		-H "Content-Type: application/json" \
		-d '{"email":"test@example.com","username":"testuser","password":"testpass123"}') && \
	echo "User created: $$USER_RESPONSE" || echo "❌ User creation failed"
	@echo ""
	@echo "2. Creating task through API Gateway..."
	@TASK_RESPONSE=$$(curl -s -X POST http://localhost:8000/tasks \
		-H "Content-Type: application/json" \
		-d '{"title":"Test Task","description":"Test Description"}') && \
	echo "Task created: $$TASK_RESPONSE" || echo "❌ Task creation failed"
	@echo ""
	@echo "3. Checking notifications..."
	@curl -s http://localhost:8000/notifications | jq . || echo "❌ Notifications not available"

# Individual service commands
start-gateway:
	@echo "Starting API Gateway..."
	docker compose up -d api-gateway

start-user:
	@echo "Starting User Service..."
	docker compose up -d user-service

start-task:
	@echo "Starting Task Service..."
	docker compose up -d task-service

start-notification:
	@echo "Starting Notification Service..."
	docker compose up -d notification-service

start-infra:
	@echo "Starting infrastructure services..."
	docker compose up -d postgres redis zookeeper kafka kafka-ui

# Utility commands
logs-gateway:
	@echo "API Gateway logs:"
	docker compose logs -f api-gateway

logs-user:
	@echo "User Service logs:"
	docker compose logs -f user-service

logs-task:
	@echo "Task Service logs:"
	docker compose logs -f task-service

logs-notification:
	@echo "Notification Service logs:"
	docker compose logs -f notification-service

logs-kafka:
	@echo "Kafka logs:"
	docker compose logs -f kafka

# Development setup
setup-dev:
	@echo "Setting up development environment..."
	make install
	make start-infra
	sleep 15
	make migrate
	@echo "Development environment ready!"

# Production-like setup
setup-prod:
	@echo "Setting up production-like environment..."
	make docker-build
	make docker-up
	sleep 30
	make health-check
	@echo "Production environment ready!"

# Cleanup
cleanup:
	@echo "Cleaning up all containers and volumes..."
	docker compose down -v
	docker system prune -f
	@echo "Cleanup complete!"

# Quick start
quick-start:
	@echo "Quick start - setting up everything..."
	make setup-dev
	make health-check
	@echo "Quick start complete! Check http://localhost:8000 for API Gateway"