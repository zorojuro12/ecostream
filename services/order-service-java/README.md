# Order Service

## Service Purpose
The Order Service is responsible for CRUD operations on orders and orchestration of the EcoStream delivery optimization platform. It manages order lifecycle, integrates with the AI forecasting service for delay predictions, and handles real-time telemetry data storage in DynamoDB.

## Tech Stack
- **Framework:** Spring Boot 3.4.0
- **Language:** Java 21
- **Database:** PostgreSQL (Orders), DynamoDB (Real-time tracking)
- **Build Tool:** Maven
- **Libraries:**
  - Spring Data JPA (PostgreSQL)
  - AWS SDK (DynamoDB)
  - Lombok (Boilerplate reduction)
  - JUnit 5 & Mockito (Testing)

## Local Setup

### Prerequisites
- Java 21
- Maven 3.8+
- Docker & Docker Compose (for PostgreSQL and DynamoDB Local)

### Running the Service

1. **Start Infrastructure:**
   ```bash
   docker-compose up -d postgres dynamodb-local
   ```

2. **Build the Service:**
   ```bash
   cd services/order-service-java
   mvn clean install
   ```

3. **Run the Service:**
   ```bash
   mvn spring-boot:run
   ```

   The service will start on port **8082**.

### Configuration
- Service port: 8082 (configured in `application.properties`)
- PostgreSQL connection: `localhost:5432` (database: `ecostream`, user: `ecostream`, password: `ecostream`)
- DynamoDB Local: `localhost:9000` (external port, 8000 internal)

## Current State

### Infrastructure
- ✅ Spring Boot application skeleton initialized
- ✅ Maven dependencies configured (Web, JPA, PostgreSQL, Lombok, AWS SDK, Validation)
- ✅ Docker Compose setup for PostgreSQL and DynamoDB Local
- ✅ Port configuration: 8082 (configured in `application.properties`)
- ✅ Database configuration: PostgreSQL connection settings configured

### Current Capabilities
- ✅ **Order Creation:** Create new orders via `POST /api/orders` with validation
  - Automatically sets order status to `PENDING` regardless of request
  - Validates coordinate ranges (latitude: -90 to 90, longitude: -180 to 180)
  - Returns created order with generated UUID
- ✅ **Order Retrieval:** Retrieve orders by ID via `GET /api/orders/{id}`
  - Returns 200 OK with order data when found
  - Returns 404 Not Found when order doesn't exist
- ✅ **Data Validation:** All API inputs validated using Jakarta Validation
  - Coordinate range validation in `LocationDTO`
  - Required field validation in `OrderRequestDTO`
- ✅ **Test Coverage:** Comprehensive unit tests using JUnit 5 and Mockito
  - Controller tests with MockMvc
  - Service tests with mocked repository
  - Entity tests for data model validation

### Implemented
- ✅ Health check endpoint (`/health`) - Returns service status (`HealthController`)
- ✅ Order Entity definition (PostgreSQL) - `Order.java`, `OrderStatus.java`
- ✅ OrderRepository - `OrderRepository.java` with custom query methods
- ✅ Data Contracts (DTOs) - `LocationDTO`, `OrderRequestDTO`, `OrderResponseDTO` with validation
- ✅ OrderService - `OrderServiceImpl` with `createOrder` and `getOrderById` methods
- ✅ Order CRUD Controller - `OrderController` with REST endpoints:
  - `POST /api/orders` - Create new order (returns 201 Created)
  - `GET /api/orders/{id}` - Retrieve order by ID (returns 200 OK or 404 Not Found)
- ⏳ DynamoDB Telemetry table setup
- ⏳ Telemetry Ingestion API
- ⏳ Integration with AI Forecasting Service

## Verified Commands

### Tool Verification
```bash
# Verify Java 21 is installed
java -version
# Expected: java version "21.0.x"

# Verify Maven is installed
mvn -version
# Expected: Apache Maven 3.8+ with Java 21
```

### Infrastructure Setup
```bash
# Start PostgreSQL and DynamoDB Local
docker-compose up -d postgres dynamodb-local

# Verify containers are healthy
docker-compose ps
# Expected: Both containers show "healthy" status

# Check container health individually
docker exec ecostream-postgres pg_isready -U ecostream
# Expected: /var/run/postgresql:5432 - accepting connections
```

### Build & Run
```bash
# Navigate to service directory
cd services/order-service-java

# Build the service (includes tests)
mvn clean install
# Expected: BUILD SUCCESS

# Run the service
mvn spring-boot:run
# Expected: Started OrderServiceApplication on port 8082
```

### Health Check
```bash
# Test health endpoint (PowerShell)
curl.exe http://localhost:8082/health
# Expected: {"status":"UP","service":"order-service"}

# Alternative (PowerShell)
Invoke-RestMethod -Uri http://localhost:8082/health
# Expected: status=UP, service=order-service
```

### Testing
```bash
# Run unit tests
mvn test
# Expected: All tests pass

# Run tests with coverage (if configured)
mvn test jacoco:report
```

## Architecture Pattern
This service follows the **Controller-Service-Repository** pattern:
- **Controllers:** Handle HTTP requests/responses (RESTful endpoints)
- **Services:** Business logic and orchestration
- **Repositories:** Data access layer (JPA for PostgreSQL, AWS SDK for DynamoDB)
