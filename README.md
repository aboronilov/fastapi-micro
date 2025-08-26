# FastAPI Microservices with Event-Driven Architecture

A FastAPI-based microservices project implementing **Domain-Driven Design (DDD)** and **Event-Driven Architecture (EDA)** with Kafka for inter-service communication.

## 🏗️ Architecture Overview

This project implements a **hybrid DDD + EDA approach**:

- **Domain-Driven Design**: Clear service boundaries with rich domain models
- **Event-Driven Architecture**: Asynchronous communication via Kafka
- **CQRS Pattern**: Command and Query Responsibility Segregation
- **Microservices**: Independent services with clear responsibilities

### Service Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Service  │    │   Task Service  │    │Notification Svc │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │   Domain    │ │    │ │   Domain    │ │    │ │   Domain    │ │
│ │  Entities   │ │    │ │  Entities   │ │    │ │  Entities   │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │Application  │ │    │ │Application  │ │    │ │Application  │ │
│ │  Commands   │ │    │ │  Commands   │ │    │ │Event Handlers│ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Kafka Event   │
                    │      Bus        │
                    └─────────────────┘
```

## 🚀 Features

- **FastAPI** framework for high-performance web APIs
- **Kafka** for event-driven communication
- **Domain-Driven Design** with rich domain models
- **Event Sourcing** with domain events
- **CQRS** pattern implementation
- **Redis** for caching
- **PostgreSQL** for data persistence
- **Docker Compose** for easy deployment
- **Poetry** for dependency management

## 📦 Installation

### Prerequisites

- Docker and Docker Compose
- Python 3.9+
- Poetry

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd fastapi-micro
```

2. **Install dependencies**
```bash
poetry install
```

3. **Start the infrastructure**
```bash
docker-compose up -d postgres redis zookeeper kafka
```

4. **Run database migrations**
```bash
poetry run alembic upgrade head
```

5. **Start the application**
```bash
poetry run uvicorn main:app --reload
```

## 🏃‍♂️ Quick Start

### Start All Services
```bash
# Start all services including Kafka UI
docker-compose up -d

# Start only core services
docker-compose up -d postgres redis zookeeper kafka fastapi-app
```

### Access Services
- **FastAPI App**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Kafka UI**: http://localhost:8080
- **pgAdmin**: http://localhost:5050 (admin@fastapi-micro.com / admin123)

### Health Checks
```bash
# System health
curl http://localhost:8000/health

# Database health
curl http://localhost:8000/health/db

# Event bus health
curl http://localhost:8000/health/events
```

## 🏛️ Domain Services

### User Service
- **Domain**: User management, authentication, profiles
- **Events**: `user.created`, `user.updated`, `user.authenticated`
- **Commands**: `CreateUser`, `UpdateUser`, `AuthenticateUser`

### Task Service
- **Domain**: Task management, categories, priorities
- **Events**: `task.created`, `task.completed`, `task.updated`
- **Commands**: `CreateTask`, `CompleteTask`, `UpdateTask`

### Notification Service
- **Domain**: Email, SMS, push notifications
- **Events**: `notification.sent`, `notification.failed`
- **Event Handlers**: Processes events from other services

## 📡 Event-Driven Communication

### Event Flow Example

1. **User Registration**
```python
# User Service publishes event
event = UserCreatedEvent(
    aggregate_id=str(user.id),
    data={"email": user.email, "username": user.username}
)
await event_bus.publish_event(event)
```

2. **Notification Service Consumes Event**
```python
# Notification Service handles event
async def handle_user_created(event: UserCreatedEvent):
    await send_welcome_email(event.data["email"])
```

### Event Topics
- `user.events` - User-related events
- `task.events` - Task-related events
- `notification.events` - Notification events
- `system.events` - System events

## 🔧 Development

### Adding New Dependencies
```bash
poetry add package-name
```

### Database Migrations
```bash
# Create new migration
poetry run alembic revision --autogenerate -m "description"

# Apply migrations
poetry run alembic upgrade head
```

### Event Development
```bash
# Create new event
# 1. Add event class in src/shared/events.py
# 2. Add to EVENT_REGISTRY
# 3. Create event handler in appropriate service
```

## 📊 Monitoring

### Kafka Topics
Access Kafka UI at http://localhost:8080 to monitor:
- Event topics and partitions
- Consumer groups
- Message flow
- Lag monitoring

### Application Logs
```bash
# View application logs
docker-compose logs -f fastapi-app

# View Kafka logs
docker-compose logs -f kafka
```

## 🧪 Testing

### Unit Tests
```bash
poetry run pytest
```

### Integration Tests
```bash
# Start test environment
docker-compose -f docker-compose.test.yml up -d

# Run integration tests
poetry run pytest tests/integration/
```

## 📚 Architecture Patterns

### Domain-Driven Design
- **Entities**: Rich domain objects with business logic
- **Value Objects**: Immutable objects representing concepts
- **Repositories**: Data access abstraction
- **Services**: Domain logic coordination

### Event-Driven Architecture
- **Event Sourcing**: Store events as source of truth
- **CQRS**: Separate read and write models
- **Event Handlers**: Process events asynchronously
- **Event Store**: Kafka as event store

### Microservices Patterns
- **API Gateway**: Single entry point (FastAPI)
- **Service Discovery**: Docker Compose networking
- **Circuit Breaker**: Resilience patterns
- **Distributed Tracing**: Event correlation

## 🔒 Security

- **JWT Authentication**: Token-based auth
- **OAuth2 Integration**: Google OAuth support
- **Password Hashing**: bcrypt for secure storage
- **Input Validation**: Pydantic models

## 🚀 Deployment

### Production Setup
```bash
# Build production image
docker build -t fastapi-micro:prod .

# Deploy with production config
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables
```bash
# Database
DB_HOST=postgres
DB_PORT=5432
DB_NAME=fastapi_micro_db
DB_USER=postgres
DB_PASSWORD=password

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:29092

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.
