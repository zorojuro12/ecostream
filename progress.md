# EcoStream Progress Tracker

## Current state (summary)
- **Order Service (Java, 8082):** CRUD + telemetry ingestion to DynamoDB; calls AI service for ETA on GET order; RestTemplate sends forecast body reliably (buffering fix).
- **AI Forecasting Service (Python, 5050):** ETA via Haversine + ML speed; `POST /api/forecast/{order_id}` for Java/dashboard; **Logistics Assistant** `POST /api/assistant/chat` — Bedrock (Claude 3.5 Haiku, us-east-1) with live distance/ETA grounding; real replies when AWS credentials in `.env`, fallback otherwise.
- **Dashboard:** Order list with Distance/ETA and red live-tracking indicator; simulation writes telemetry to DynamoDB; **Logistics Assistant** floating chat (select order → ask context-aware questions; calls POST /api/assistant/chat).
- **Remaining:** GitHub Actions CI/CD and AWS Lambda migration.

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
- [x] Develop ETA calculation logic (Distance/Time).
- [x] **VERIFIED:** Haversine distance engine tested with SFU campuses (13.72 km accuracy).
- [x] **VERIFIED:** Base forecasting service with constant speed (40 km/h) placeholder.
- [x] **VERIFIED:** Forecasting API endpoint (`POST /api/forecast/{order_id}`) functional.
- [x] Integrate Scikit-Learn model for delay prediction.
- [x] Connect Java Order Service to Python AI Service.
- [x] **VERIFIED:** Forecast POST body fix — Order Service uses `BufferingClientHttpRequestFactory` so the JSON body is sent reliably to the AI service (Spring 6.1.x default could set Content-Length but not write body bytes). Dashboard now shows Distance (km), ETA (min), and red live-tracking indicator for orders when simulation runs.

## Phase 4: AWS & Full-Stack Dashboard
- [x] Integrate Amazon Bedrock for "Logistics Assistant." (boto3 Converse API, Claude 3.5 Haiku, us-east-1; data grounding with distance/ETA; POST /api/assistant/chat; AccessDenied fallback)
- [x] **VERIFIED:** Logistics Assistant returns real Bedrock replies when AWS credentials are set in `.env`; `get_bedrock_client()` loads .env (service + repo root) so the running app has the same credentials as `scripts/aws-test.py`.
- [x] Initialize TypeScript/React Dashboard (Vite, Vitest, Tailwind, Order List with ETA, Refresh, loading/error states).
- [x] Real-time telemetry visualization (live polling, movement simulator, blinking pulse when ETA + auto-refresh).
- [x] **End-to-end GenAI:** Dashboard Logistics Assistant chat box (floating bubble → dark chat window; select order, send message to Bedrock-backed assistant; auto-scroll, selection-aware placeholder).
- [ ] Setup GitHub Actions (CI/CD) and AWS Lambda migration.
