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
- [x] Implement OrderService (full CRUD operations implemented with TDD).
- [x] Implement Basic CRUD Controller (all endpoints: POST, GET all, GET by ID, PUT, DELETE).
- [x] Setup DynamoDB Telemetry Table (Real-time tracking).
- [x] Implement Telemetry data layer (Telemetry entity, TelemetryRepository, DynamoDB config).
- [x] Implement Telemetry Ingestion API (Java -> DynamoDB).

## Phase 3: AI & Forecasting (The "Brain")
- [x] Initialize FastAPI service and package structure (/app).
- [x] Establish environment config (.env) and dependency management.
- [x] Implement Location schema with strict Java parity ([-90,90], [-180,180]).
- [x] Implement DynamoDB Telemetry Reader service.
- [ ] Develop ETA calculation logic (Distance/Time). (Next)
- [ ] Integrate Scikit-Learn model for delay prediction.
- [ ] Connect Java Order Service to Python AI Service.

## Phase 4: AWS & Full-Stack Dashboard
- [ ] Integrate Amazon Bedrock for "Logistics Assistant."
- [ ] Build TypeScript/React Dashboard.
- [ ] Setup GitHub Actions (CI/CD) and AWS Lambda migration.
