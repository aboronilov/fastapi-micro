# Microservices Architecture with API Gateway

## 🏗️ **Architecture Overview**

This project has been refactored to implement a **true microservices architecture** with an **API Gateway** pattern. The new structure separates concerns, enables independent deployment, and provides better scalability and maintainability.

### **Architecture Diagram**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT APPLICATIONS                            │
└─────────────────────┬───────────────────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────────────────┐
│                              API GATEWAY                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ • Request Routing & Load Balancing                                  │   │
│  │ • Authentication & Authorization                                    │   │
│  │ • Rate Limiting                                                     │   │
│  │ • Service Discovery & Health Checks                                 │   │
│  │ • Request/Response Transformation                                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────────────────────┘
                      │
    ┌─────────────────┼─────────────────┐
    │                 │                 │
┌───▼────┐    ┌──────▼──────┐    ┌─────▼─────┐
│ USER   │    │   TASK     │    │NOTIFICATION│
│SERVICE │    │  SERVICE   │    │  SERVICE  │
│(8001)  │    │   (8002)   │    │   (8003)  │
└────────┘    └────────────┘    └───────────┘
    │                 │                 │
    └─────────────────┼─────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────────────────┐
│                              SHARED INFRASTRUCTURE                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │ PostgreSQL  │  │    Redis    │  │   Kafka     │  │  Zookeeper  │       │
│  │  Database   │  │    Cache    │  │ Event Bus   │  │   Cluster   │       │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘       │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 📁 **New Project Structure**

```
fastapi-micro/
├── gateway/                          # API Gateway
│   ├── __init__.py
│   └── main.py                      # Gateway application
├── services/                         # Individual microservices
│   ├── user-service/
│   │   └── main.py                  # User service application
│   ├── task-service/
│   │   └── main.py                  # Task service application
│   └── notification-service/
│       └── main.py                  # Notification service application
├── src/                             # Shared domain logic
│   ├── services/                    # Domain services
│   │   ├── user/                    # User domain
│   │   │   ├── domain/             # Domain layer
│   │   │   ├── infrastructure/     # Infrastructure layer
│   │   │   ├── application/        # Application layer
│   │   │   └── api/                # API layer
│   │   ├── task/                   # Task domain
│   │   └── notification/           # Notification domain
│   ├── shared/                     # Shared components
│   │   ├── events.py              # Domain events
│   │   └── kafka_client.py        # Kafka client
│   ├── integration/                # Service integration
│   ├── database/                   # Database layer
│   ├── dependencies.py             # Dependency injection
│   └── event_bus.py               # Event bus
├── docker-compose.yml              # Microservices orchestration
├── Dockerfile.gateway              # Gateway container
├── Dockerfile.service              # Service containers
├── Dockerfile                      # Legacy container
└── README.md                       # Project documentation
```

## 🚀 **Services Overview**

### **1. API Gateway (Port 8000)**
- **Purpose**: Single entry point for all client requests
- **Features**:
  - Request routing to appropriate microservices
  - Authentication and authorization
  - Rate limiting (100 requests/minute per IP)
  - Service health monitoring
  - Request/response transformation
  - Error handling and logging

### **2. User Service (Port 8001)**
- **Purpose**: User management and authentication
- **Endpoints**:
  - `POST /users` - Create user
  - `GET /users` - List users
  - `GET /users/{id}` - Get user
  - `PUT /users/{id}` - Update user
  - `POST /auth/verify` - Verify JWT token
- **Events Published**: `UserCreatedEvent`, `UserUpdatedEvent`

### **3. Task Service (Port 8002)**
- **Purpose**: Task management and workflow
- **Endpoints**:
  - `POST /tasks` - Create task
  - `GET /tasks` - List tasks
  - `GET /tasks/{id}` - Get task
  - `PUT /tasks/{id}` - Update task
  - `POST /tasks/{id}/complete` - Complete task
  - `DELETE /tasks/{id}` - Delete task
- **Events Published**: `TaskCreatedEvent`, `TaskCompletedEvent`, `TaskUpdatedEvent`

### **4. Notification Service (Port 8003)**
- **Purpose**: Notification management and delivery
- **Endpoints**:
  - `POST /notifications` - Create notification
  - `GET /notifications` - List notifications
  - `GET /notifications/{id}` - Get notification
  - `POST /notifications/{id}/send` - Send notification
  - `DELETE /notifications/{id}` - Delete notification
- **Events Consumed**: `UserCreatedEvent`, `TaskCompletedEvent`
- **Events Published**: `NotificationSentEvent`

## 🔧 **Key Features**

### **API Gateway Features**

#### **1. Service Discovery**
```python
SERVICES = {
    "user": {
        "url": "http://user-service:8001",
        "health_check": "/health",
        "routes": ["/users", "/auth"]
    },
    "task": {
        "url": "http://task-service:8002", 
        "health_check": "/health",
        "routes": ["/tasks", "/categories"]
    },
    "notification": {
        "url": "http://notification-service:8003",
        "health_check": "/health", 
        "routes": ["/notifications"]
    }
}
```

#### **2. Request Routing**
- Dynamic routing based on URL paths
- Automatic service discovery
- Health check before forwarding requests
- Load balancing (round-robin)

#### **3. Rate Limiting**
- 100 requests per minute per IP address
- Configurable limits
- Automatic cleanup of old requests

#### **4. Authentication**
- JWT token verification
- Token forwarding to user service
- Authorization header preservation

### **Event-Driven Communication**

#### **Event Flow Example**
1. **User Registration**:
   ```
   Client → API Gateway → User Service → UserCreatedEvent → Notification Service
   ```

2. **Task Completion**:
   ```
   Client → API Gateway → Task Service → TaskCompletedEvent → Notification Service
   ```

#### **Kafka Topics**
- `user.events` - User-related events
- `task.events` - Task-related events
- `notification.events` - Notification events
- `system.events` - System events

## 🐳 **Docker Configuration**

### **Service Containers**
Each microservice runs in its own container with:
- Independent health checks
- Service-specific environment variables
- Dedicated ports
- Shared network for inter-service communication

### **Infrastructure Services**
- **PostgreSQL**: Shared database
- **Redis**: Shared cache
- **Kafka**: Event bus
- **Zookeeper**: Kafka cluster management
- **Kafka UI**: Event monitoring

## 📊 **Health Monitoring**

### **API Gateway Health Check**
```bash
curl http://localhost:8000/health
```
Response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "services": {
    "user": "healthy",
    "task": "healthy", 
    "notification": "healthy"
  }
}
```

### **Individual Service Health Checks**
```bash
# User Service
curl http://localhost:8001/health

# Task Service  
curl http://localhost:8002/health

# Notification Service
curl http://localhost:8003/health
```

## 🚀 **Deployment**

### **Start All Services**
```bash
# Start all services including API Gateway
docker compose up -d

# Start only infrastructure
docker compose up -d postgres redis zookeeper kafka

# Start only microservices
docker compose up -d api-gateway user-service task-service notification-service
```

### **Service URLs**
- **API Gateway**: http://localhost:8000
- **User Service**: http://localhost:8001
- **Task Service**: http://localhost:8002
- **Notification Service**: http://localhost:8003
- **Kafka UI**: http://localhost:8080

### **API Documentation**
- **API Gateway**: http://localhost:8000/docs
- **User Service**: http://localhost:8001/docs
- **Task Service**: http://localhost:8002/docs
- **Notification Service**: http://localhost:8003/docs

## 🔄 **Migration from Monolithic**

### **Benefits of New Architecture**

#### **1. Scalability**
- Services can scale independently
- Load balancing at API Gateway level
- Horizontal scaling per service

#### **2. Maintainability**
- Clear service boundaries
- Independent development and deployment
- Technology diversity per service

#### **3. Resilience**
- Service isolation
- Circuit breaker patterns
- Graceful degradation

#### **4. Development Velocity**
- Parallel development teams
- Independent release cycles
- Reduced deployment risk

### **Backward Compatibility**
- Legacy monolithic app still available on port 8004
- Gradual migration path
- Shared domain logic in `src/` directory

## 🛠️ **Development Workflow**

### **Adding New Services**
1. Create service directory in `services/`
2. Implement service-specific logic
3. Add service configuration to API Gateway
4. Update Docker Compose
5. Add health checks and monitoring

### **Service Communication**
- **Synchronous**: HTTP requests through API Gateway
- **Asynchronous**: Events through Kafka
- **Service-to-Service**: Direct HTTP calls (internal network)

### **Testing Strategy**
- **Unit Tests**: Per service
- **Integration Tests**: Service boundaries
- **End-to-End Tests**: Full workflow through API Gateway
- **Event Tests**: Kafka event flow validation

## 📈 **Monitoring & Observability**

### **Logging**
- Structured logging per service
- Request tracing through API Gateway
- Event correlation IDs

### **Metrics**
- Request/response times
- Error rates per service
- Event processing metrics
- Resource utilization

### **Tracing**
- Distributed tracing across services
- Request flow visualization
- Performance bottleneck identification

## 🔒 **Security**

### **API Gateway Security**
- Rate limiting
- Request validation
- Authentication forwarding
- CORS configuration

### **Service Security**
- Internal network isolation
- Service-to-service authentication
- Environment variable management
- Secrets management

## 🎯 **Next Steps**

### **Immediate Improvements**
1. **Service Mesh**: Implement Istio or Linkerd
2. **Centralized Logging**: ELK stack integration
3. **Metrics Collection**: Prometheus + Grafana
4. **CI/CD Pipeline**: Automated deployment
5. **Service Discovery**: Consul or etcd integration

### **Advanced Features**
1. **Circuit Breakers**: Resilience patterns
2. **API Versioning**: Backward compatibility
3. **Caching Strategy**: Redis integration
4. **Database Per Service**: Data isolation
5. **Event Sourcing**: Complete audit trail

This microservices architecture provides a solid foundation for scalable, maintainable, and resilient applications with clear separation of concerns and independent service deployment capabilities.
