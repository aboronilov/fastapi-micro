# FastAPI Microservice - Docker Setup

This document explains how to run the FastAPI microservice using Docker Compose.

## Prerequisites

- Docker
- Docker Compose

## Quick Start

### 1. Start the entire stack

```bash
# Start all services (FastAPI app + PostgreSQL)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### 2. Start with database management tools

```bash
# Start with pgAdmin (database management UI)
docker-compose --profile tools up -d

# Access pgAdmin at: http://localhost:5050
# Email: admin@fastapi-micro.com
# Password: admin123
```

## Services

### FastAPI Application
- **Container**: `fastapi-micro`
- **Port**: `8000`
- **Health Check**: `http://localhost:8000/health/db`
- **API Documentation**: `http://localhost:8000/docs`

### PostgreSQL Database
- **Container**: `fastapi-postgres`
- **Port**: `5432`
- **Database**: `fastapi_micro_db`
- **User**: `postgres`
- **Password**: `password`

### Redis Cache
- **Container**: `fastapi-redis`
- **Port**: `6379`
- **Health Check**: `http://localhost:8000/redis/health`
- **Info**: `http://localhost:8000/redis/info`

### pgAdmin (Optional)
- **Container**: `fastapi-pgadmin`
- **Port**: `5050`
- **Email**: `admin@fastapi-micro.com`
- **Password**: `admin123`

## Environment Variables

The application uses the following environment variables (configured in docker-compose.yml):

```yaml
# Database Configuration
DB_HOST: postgres
DB_PORT: 5432
DB_NAME: fastapi_micro_db
DB_USER: postgres
DB_PASSWORD: password

# Application Configuration
HOST: 0.0.0.0
PORT: 8000
```

## Volumes

- `postgres_data`: PostgreSQL data persistence
- `pgadmin_data`: pgAdmin configuration persistence
- `./src`: Application source code (read-only)
- `./alembic`: Migration files (read-only)

## Networks

All services run on the `fastapi-network` bridge network for secure inter-service communication.

## Development Workflow

### 1. First-time setup

```bash
# Build and start services
docker-compose up --build

# The application will automatically:
# - Wait for PostgreSQL to be ready
# - Run database migrations
# - Start the FastAPI server
```

### 2. Development with hot reload

```bash
# Start services in development mode
docker-compose up

# The FastAPI app runs with --reload flag
# Code changes will automatically restart the server
```

### 3. Database operations

```bash
# Run migrations manually
docker-compose exec fastapi-app poetry run alembic upgrade head

# Create new migration
docker-compose exec fastapi-app poetry run alembic revision --autogenerate -m "description"

# Seed database
docker-compose exec fastapi-app poetry run python -c "from src.database.seeder import seed_database; from src.database.config import SessionLocal; db = SessionLocal(); seed_database(db); db.close()"
```

### 4. Viewing logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f fastapi-app
docker-compose logs -f postgres
```

## Testing the API

Once the services are running, you can test the API:

```bash
# Health check
curl http://localhost:8000/health/db

# Get all tasks
curl http://localhost:8000/task/all

# Create a new task
curl -X POST http://localhost:8000/task/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Task", "description": "Test description", "pomodoro_count": 4}'
```

## Troubleshooting

### 1. Database connection issues

```bash
# Check if PostgreSQL is running
docker-compose ps

# Check PostgreSQL logs
docker-compose logs postgres

# Connect to database manually
docker-compose exec postgres psql -U postgres -d fastapi_micro_db
```

### 2. Application startup issues

```bash
# Check application logs
docker-compose logs fastapi-app

# Restart application only
docker-compose restart fastapi-app

# Rebuild and restart
docker-compose up --build fastapi-app
```

### 3. Migration issues

```bash
# Check migration status
docker-compose exec fastapi-app poetry run alembic current

# Reset database (WARNING: This will delete all data)
docker-compose down -v
docker-compose up --build
```

## Production Considerations

For production deployment, consider:

1. **Security**:
   - Change default passwords
   - Use secrets management
   - Enable SSL/TLS
   - Restrict network access

2. **Performance**:
   - Use production-grade PostgreSQL configuration
   - Configure connection pooling
   - Enable query optimization

3. **Monitoring**:
   - Add logging aggregation
   - Set up metrics collection
   - Configure alerting

4. **Backup**:
   - Set up automated database backups
   - Test restore procedures

## Cleanup

```bash
# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes (WARNING: deletes data)
docker-compose down -v

# Remove images
docker-compose down --rmi all
```
