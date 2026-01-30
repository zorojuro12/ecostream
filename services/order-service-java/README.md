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

   The service will start on port **8080**.

### Configuration
- PostgreSQL connection: `localhost:5432` (database: `ecostream`, user: `ecostream`, password: `ecostream`)
- DynamoDB Local: `localhost:9000`

## Current State

### Infrastructure
- ✅ Spring Boot application skeleton initialized
- ✅ Maven dependencies configured (Web, JPA, PostgreSQL, Lombok)
- ✅ Docker Compose setup for PostgreSQL and DynamoDB Local

### Pending Implementation
- ⏳ Health check endpoint (`/health`)
- ⏳ Order Entity definition (PostgreSQL)
- ⏳ OrderRepository and CRUD Controller
- ⏳ DynamoDB Telemetry table setup
- ⏳ Telemetry Ingestion API
- ⏳ Integration with AI Forecasting Service

## Architecture Pattern
This service follows the **Controller-Service-Repository** pattern:
- **Controllers:** Handle HTTP requests/responses (RESTful endpoints)
- **Services:** Business logic and orchestration
- **Repositories:** Data access layer (JPA for PostgreSQL, AWS SDK for DynamoDB)
