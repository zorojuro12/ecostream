# EcoStream Progress Tracker

## Phase 1: Foundation (Scaffolding & Infrastructure)
- [x] Create project directory structure.
- [x] Initialize Java (Spring Boot) and Python (FastAPI) skeletons.
- [x] Setup Docker Compose for PostgreSQL and DynamoDB Local.
- [x] Verify inter-service connectivity (Health Checks).
- [x] Configure application.properties with port 8082.
- [x] Implement HealthController for Order Service.
- [x] Add AWS SDK dependency for DynamoDB.
- [x] Update .gitignore for polyglot microservices.

## Phase 2: Core Data & Logic (The "Order" System)
- [x] Define the `Order` Entity in Java (PostgreSQL).
- [x] Implement `OrderRepository` interface.
- [x] Establish data contracts (DTOs) and validation.
- [ ] Implement OrderService (in progress: createOrder implemented with TDD).
- [ ] Implement Basic CRUD Controller.
- [ ] Setup DynamoDB Telemetry Table (Real-time tracking).
- [ ] Implement Telemetry Ingestion API (Java -> DynamoDB).

## Phase 3: AI & Forecasting (The "Brain")
- [ ] Setup Scikit-Learn model in Python service.
- [ ] Implement `/predict/delay` endpoint in Python.
- [ ] Connect Java Order Service to Python AI Service.

## Phase 4: AWS & Full-Stack Dashboard
- [ ] Integrate Amazon Bedrock for "Logistics Assistant."
- [ ] Build TypeScript/React Dashboard.
- [ ] Setup GitHub Actions (CI/CD) and AWS Lambda migration.
