# Testing Guide for Microservices Architecture

## 🧪 **Testing Strategy Overview**

This project follows a comprehensive testing strategy that covers all layers of the microservices architecture. Tests are organized in a separate `tests/` directory to maintain clean separation between application code and test code.

## 📁 **Test Structure**

```
tests/
├── unit/                          # Unit tests for domain logic
│   ├── services/
│   │   ├── user/                  # User service unit tests
│   │   │   ├── test_domain_entities.py
│   │   │   ├── test_application_handlers.py
│   │   │   └── test_infrastructure_repositories.py
│   │   ├── task/                  # Task service unit tests
│   │   └── notification/          # Notification service unit tests
│   └── shared/                    # Shared components unit tests
│       ├── test_events.py
│       └── test_kafka_client.py
├── integration/                   # Integration tests
│   ├── test_user_service_api.py
│   ├── test_task_service_api.py
│   ├── test_notification_service_api.py
│   ├── test_gateway.py
│   └── test_microservices_communication.py
└── fixtures/                      # Shared test fixtures
    ├── test_data.py
    ├── mock_services.py
    └── test_containers.py
```

## 🎯 **Test Types**

### **1. Unit Tests**
- **Purpose**: Test individual components in isolation
- **Scope**: Domain entities, value objects, application handlers, business logic
- **Dependencies**: Mocked external dependencies
- **Speed**: Fast execution
- **Location**: `tests/unit/`

**Example Unit Test Structure:**
```python
@pytest.mark.unit
class TestUserEntity:
    def test_create_user_with_valid_data(self):
        # Arrange
        user_data = {"email": "test@example.com", "username": "testuser"}
        
        # Act
        user = User.create(**user_data, password="password123")
        
        # Assert
        assert user.email == user_data["email"]
        assert user.username == user_data["username"]
        assert user.verify_password("password123") is True
```

### **2. Integration Tests**
- **Purpose**: Test service APIs and inter-service communication
- **Scope**: API endpoints, database operations, external service integration
- **Dependencies**: Real or test databases, mocked external services
- **Speed**: Medium execution time
- **Location**: `tests/integration/`

**Example Integration Test Structure:**
```python
@pytest.mark.integration
class TestUserServiceAPI:
    def test_create_user_success(self, client, mock_user_repository):
        # Arrange
        user_data = {"email": "test@example.com", "username": "testuser"}
        
        # Act
        response = client.post("/users", json=user_data)
        
        # Assert
        assert response.status_code == 201
        assert response.json()["email"] == user_data["email"]
```

### **3. End-to-End Tests**
- **Purpose**: Test complete user workflows across multiple services
- **Scope**: Full system integration, user journeys
- **Dependencies**: All services running, real infrastructure
- **Speed**: Slow execution
- **Location**: `tests/e2e/`

## 🚀 **Running Tests**

### **Install Test Dependencies**
```bash
# Install pytest and testing dependencies
pip install pytest pytest-asyncio pytest-mock httpx

# For coverage reporting
pip install pytest-cov
```

### **Run All Tests**
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src --cov-report=html
```

### **Run Specific Test Types**
```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only slow tests
pytest -m slow

# Run only end-to-end tests
pytest -m e2e
```

### **Run Tests for Specific Service**
```bash
# Run user service tests
pytest tests/unit/services/user/
pytest tests/integration/test_user_service_api.py

# Run task service tests
pytest tests/unit/services/task/
pytest tests/integration/test_task_service_api.py

# Run notification service tests
pytest tests/unit/services/notification/
pytest tests/integration/test_notification_service_api.py
```

### **Run Tests with Specific Patterns**
```bash
# Run tests matching a pattern
pytest -k "user"

# Run tests in a specific file
pytest tests/unit/services/user/test_domain_entities.py

# Run a specific test method
pytest tests/unit/services/user/test_domain_entities.py::TestUserEntity::test_create_user_with_valid_data
```

## 🛠️ **Test Configuration**

### **Environment Variables**
Tests use separate environment variables to avoid affecting production:

```bash
# Test environment variables
export TESTING=true
export DATABASE_URL=postgresql://test_user:test_password@localhost:5432/test_db
export REDIS_URL=redis://localhost:6379/1
export KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```

### **Pytest Configuration**
The `pytest.ini` file configures:
- Test discovery patterns
- Markers for different test types
- Output formatting
- Environment variables

## 📊 **Test Coverage**

### **Coverage Goals**
- **Unit Tests**: 90%+ coverage for domain logic
- **Integration Tests**: 80%+ coverage for API endpoints
- **End-to-End Tests**: Critical user workflows

### **Generate Coverage Report**
```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html
```

## 🔧 **Test Fixtures and Utilities**

### **Shared Test Data**
The `tests/fixtures/test_data.py` file provides:
- Sample entities for all services
- Test events and data structures
- Invalid data for negative testing
- Configuration for test environments

### **Mock Services**
The `tests/fixtures/mock_services.py` file provides:
- Mocked external services
- Database connection mocks
- Event bus mocks
- Authentication mocks

### **Test Containers**
The `tests/fixtures/test_containers.py` file provides:
- Database containers for integration tests
- Redis containers for caching tests
- Kafka containers for event testing

## 📝 **Writing Tests**

### **Unit Test Guidelines**
1. **Arrange-Act-Assert**: Structure tests with clear sections
2. **Descriptive Names**: Use descriptive test method names
3. **Single Responsibility**: Each test should test one thing
4. **Mock Dependencies**: Mock external dependencies
5. **Test Edge Cases**: Include positive and negative test cases

### **Integration Test Guidelines**
1. **Test Real APIs**: Use FastAPI TestClient for API testing
2. **Database State**: Clean up database state between tests
3. **Service Isolation**: Test one service at a time
4. **Error Scenarios**: Test error handling and edge cases

### **Test Naming Conventions**
```python
# Unit tests
def test_create_user_with_valid_data(self):
def test_create_user_with_invalid_email_raises_error(self):
def test_user_password_verification(self):

# Integration tests
def test_user_service_api_create_user_success(self):
def test_user_service_api_create_user_validation_error(self):
def test_user_service_api_database_connection_error(self):
```

## 🐛 **Debugging Tests**

### **Running Tests in Debug Mode**
```bash
# Run with detailed output
pytest -v -s

# Run with print statements
pytest -s

# Run with pdb debugger
pytest --pdb
```

### **Common Test Issues**
1. **Import Errors**: Ensure `src/` is in Python path
2. **Database Issues**: Check test database configuration
3. **Mock Issues**: Verify mock setup and assertions
4. **Async Issues**: Use `pytest-asyncio` for async tests

## 🔄 **Continuous Integration**

### **GitHub Actions Example**
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```

## 📚 **Best Practices**

### **Test Organization**
1. **Group by Service**: Organize tests by microservice
2. **Group by Layer**: Separate unit, integration, and e2e tests
3. **Shared Fixtures**: Use shared fixtures for common test data
4. **Clear Structure**: Follow consistent naming and organization

### **Test Data Management**
1. **Isolation**: Each test should be independent
2. **Cleanup**: Clean up test data after each test
3. **Realistic Data**: Use realistic but safe test data
4. **Variety**: Test with different data scenarios

### **Performance Considerations**
1. **Fast Unit Tests**: Keep unit tests fast (< 100ms each)
2. **Parallel Execution**: Use pytest-xdist for parallel test execution
3. **Database Optimization**: Use transactions for database tests
4. **Mock Heavy Operations**: Mock slow external services

## 🎯 **Next Steps**

1. **Add More Tests**: Expand test coverage for all services
2. **Performance Tests**: Add load and performance testing
3. **Security Tests**: Add security-focused test cases
4. **Monitoring**: Add test result monitoring and reporting
5. **Documentation**: Keep test documentation up to date

This testing strategy ensures that your microservices are reliable, maintainable, and ready for production deployment.
