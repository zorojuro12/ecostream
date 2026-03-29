# EcoStream Technical Specification

## System Overview

EcoStream is a **serverless-ready, polyglot microservices platform** utilizing **GenAI for logistics optimization**. It delivers last-mile delivery optimization by combining real-time telemetry, ML-based ETA forecasting, and a context-aware Logistics Assistant (Claude via Amazon Bedrock). The system is implemented for local development today with a clear path to AWS cloud deployment.

---

## Architecture Map

### Current Local Setup

| Component | Technology | Port | Responsibility |
|-----------|------------|------|----------------|
| **Order Service** | Java 21, Spring Boot 3.4 | **8082** | CRUD for orders (PostgreSQL), telemetry ingestion (DynamoDB), orchestration; enriches GET order with ETA from AI service. Resilience4j circuit breaker on AI client; Actuator health/info/CB-state endpoints. |
| **AI Forecasting Service** | Python 3.x, FastAPI | **5050** | ETA (Haversine + RandomForest ML model), `POST /api/forecast/{order_id}`; Logistics Assistant `POST /api/assistant/chat` (Bedrock Converse API, Claude 3.5 Haiku, us-east-1); S3 forecast logging (fire-and-forget). |
| **PostgreSQL** | Docker | 5432 | Order persistence (Single Source of Truth for order and destination). |
| **DynamoDB Local** | Docker | **9000** (external) | Telemetry table `ecostream-telemetry-local` (partition: orderId, sort: timestamp). |
| **Dashboard** | TypeScript, React, Vite, Tailwind | **5173** (Vite dev) | Order list with Distance/ETA and live-tracking indicator; **live delivery map** (Leaflet.js, CARTO dark tiles, vehicle/destination markers, route polyline); floating Logistics Assistant chat. |

- **Order Service** calls AI service at `ai.forecasting.base-url` (default `http://localhost:5050`) for forecast and uses DynamoDB at `http://localhost:9000`.
- **Dashboard** calls Order Service at `http://localhost:8082` for orders, AI service at `http://localhost:5050` for assistant chat and live telemetry (map).

### Target Cloud Architecture

| AWS Service | Purpose |
|-------------|---------|
| **API Gateway** | Single entry point for orders, telemetry, and (optionally) assistant; rate limiting and auth. |
| **AWS Lambda** | Python AI service (forecast + assistant) as serverless functions; event-driven scaling. Mangum adapter + `Dockerfile.lambda` already built. |
| **Amazon RDS (PostgreSQL)** | Managed Order persistence; same schema as local. Order Service `application.properties` is environment-aware (`${DB_URL}`, `${DB_USER}`, `${DB_PASSWORD}` with local defaults). |
| **Amazon DynamoDB** | Managed telemetry table; same key schema (orderId PK, timestamp SK). Python client switches automatically when `EXECUTION_ENV=lambda`. |
| **Amazon S3** | Forecast audit logs (`delivery-logs/forecasts/{order_id}_{timestamp}.json`), training data, static assets. Logger wired into forecast flow (fire-and-forget, no-op when `S3_LOG_BUCKET` unset). |
| **Amazon Bedrock** | Logistics Assistant (Converse API, Claude 3.5 Haiku, us-east-1). Already integrated; grounded with live distance/ETA context. |
| **CloudWatch** | Logs, metrics, and alarms for all services. |

- Migration path: Order Service can remain on ECS/EC2 or move to Lambda/container; AI service is Lambda-ready (Mangum + Dockerfile.lambda). Dashboard can be hosted on S3 + CloudFront.

---

## Core Data Models

The **Java Order Service** is the **Single Source of Truth (SSoT)** for order identity, destination, and priority. The AI service and dashboard consume or reference this data via APIs; they do not maintain their own copy of order master data.

### Order (PostgreSQL – Order Service)

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key, generated. |
| `status` | Enum | `PENDING`, `CONFIRMED`, `IN_TRANSIT`, `DELIVERED`, `CANCELLED`. |
| `destinationLatitude` | Double | -90 to 90 (inclusive). |
| `destinationLongitude` | Double | -180 to 180 (inclusive). |
| `priority` | Integer | Higher = higher priority (e.g. ≥5 → Express for ML speed). |

**API response (OrderResponseDTO)** also includes enriched fields when AI is available: `destination` (lat/lon), `priority`, `distanceKm`, `estimatedArrivalMinutes` (null if AI unavailable — circuit breaker fallback).

### Telemetry (DynamoDB – Order Service writes; AI Service reads)

| Field | Type | Key | Description |
|-------|------|-----|-------------|
| `orderId` | String | Partition Key | Links to Order. |
| `timestamp` | Long | Sort Key | Epoch seconds. |
| `currentLatitude` | Double | — | -90 to 90. |
| `currentLongitude` | Double | — | -180 to 180. |

- Table name (local): `ecostream-telemetry-local`. Ingress: `POST /api/orders/{id}/telemetry` (Order Service). ETA and assistant use latest telemetry per order.

### Location (shared validation)

- **Latitude:** -90 to 90 (inclusive).  
- **Longitude:** -180 to 180 (inclusive).  
- Enforced in Java (Jakarta Validation), Python (Pydantic), and API contracts.

---

## ML & AI Models

### ETA Speed Prediction (Scikit-Learn)

| Property | Value |
|----------|-------|
| **Algorithm** | RandomForestRegressor (via Scikit-Learn Pipeline with ColumnTransformer) |
| **Training data** | NYC Taxi Trip Duration (Kaggle, 1.46M trips), downsampled to 20k rows |
| **Features** | `distance_km`, `hour_of_day`, `day_of_week`, `month`, `priority` (Express/Standard) |
| **Target** | `speed_kmh` (derived: distance / duration) |
| **Evaluation** | MAE 4.24 km/h, RMSE 5.79 km/h, R² 0.45 |
| **Artifact** | `models/speed_model.joblib` (committed) |
| **Fallback** | Time-aware heuristic if model file is missing (rush-hour/off-peak/Express adjustments) |

ETA is computed as `distance_km / predicted_speed_kmh * 60` (minutes). Time features are derived from `datetime.now(UTC)` at request time.

### Logistics Assistant (Amazon Bedrock)

| Property | Value |
|----------|-------|
| **API** | boto3 Converse API (`client.converse()`) |
| **Model** | `us.anthropic.claude-3-5-haiku-20241022-v1:0` (US inference profile, us-east-1) |
| **Identity** | System prompt defines AI as "EcoStream Logistics Assistant" |
| **Grounding** | Live distance + ETA injected via XML tags: `<context>Distance: {d}km, ETA: {e}min</context>` |
| **Fallback** | On `AccessDeniedException`: friendly mock response |

The assistant fetches order data from the Order Service (SSoT), computes distance/ETA from telemetry + Haversine, and injects this context into the system prompt before calling Bedrock.

---

## Resilience & Observability

### Circuit Breaker (Resilience4j – Order Service)

The `ForecastingClientImpl.getForecast()` call is wrapped with `@CircuitBreaker(name = "forecastService")`:

| Config | Value | Rationale |
|--------|-------|-----------|
| `slidingWindowSize` | 10 | Count-based; low request volume makes time-based impractical |
| `failureRateThreshold` | 50% | Open after 5 of 10 failures |
| `waitDurationInOpenState` | 10s | Cooldown before probing |
| `permittedNumberOfCallsInHalfOpenState` | 3 | Probe attempts in HALF_OPEN |
| `minimumNumberOfCalls` | 5 | Don't evaluate until sufficient sample |

**Fallback:** Returns `null` → `enrichWithForecast` serves the order without ETA fields. Graceful degradation.

### Spring Boot Actuator (Order Service)

| Endpoint | Purpose |
|----------|---------|
| `GET /actuator/health` | Health check with circuit breaker state (UP/DOWN/CIRCUIT_OPEN) |
| `GET /actuator/info` | Service info metadata |
| `GET /actuator/circuitbreakers` | Circuit breaker registry with current state and metrics |

### S3 Forecast Logging (AI Service)

Every successful `calculate_eta()` call fires `upload_forecast_log()` — a JSON payload (`order_id`, `distance_km`, `estimated_arrival_minutes`, `priority`, `timestamp_utc`) uploaded to `s3://{S3_LOG_BUCKET}/delivery-logs/forecasts/{order_id}_{timestamp}.json`. Fire-and-forget: no-op when `S3_LOG_BUCKET` is empty (local dev), silent failure on upload error.

---

## Integration Contracts (APIs)

### Order Service (Java) – base URL local: `http://localhost:8082`

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/orders` | List all orders. |
| `GET` | `/api/orders/{id}` | Get order by ID. **Enriched** with `distanceKm` and `estimatedArrivalMinutes` from AI service (POST /api/forecast/{order_id}). Returns null ETA fields if AI service is down (circuit breaker fallback). 404 if not found. |
| `POST` | `/api/orders` | Create order (body: destination, priority, etc.). Returns 201 with order. |
| `PUT` | `/api/orders/{id}` | Update order (partial). |
| `DELETE` | `/api/orders/{id}` | Delete order. 204 on success. |
| `POST` | `/api/orders/{id}/telemetry` | Ingest telemetry. Body: `{ "latitude", "longitude" }` (current position). Order Service generates timestamp and writes to DynamoDB. 202 Accepted. |
| `GET` | `/actuator/health` | Health check including circuit breaker state. |
| `GET` | `/actuator/info` | Service info. |
| `GET` | `/actuator/circuitbreakers` | Circuit breaker registry (state, metrics). |

### AI Forecasting Service (Python) – base URL local: `http://localhost:5050`

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check. |
| `GET` | `/api/test/telemetry/{order_id}` | Latest telemetry position for an order. Returns `{ "latitude", "longitude" }` or 404. Used by dashboard for live map. |
| `POST` | `/api/forecast/{order_id}` | **ETA forecast.** Body: `destination_latitude`, `destination_longitude`, `priority` (optional, default "Standard"). Returns `{ "distance_km", "estimated_arrival_minutes" }`. Logs result to S3 (fire-and-forget). 404 if no telemetry for order. Called by Order Service when enriching GET /api/orders/{id}. |
| `POST` | `/api/assistant/chat` | **Logistics Assistant (GenAI).** Body: `order_id`, `message`. AI service fetches order from Order Service (SSoT), computes distance/ETA from telemetry + Haversine, injects context into system prompt, and calls **Bedrock Converse API** (Claude 3.5 Haiku, us-east-1). Returns `{ "reply": "..." }`. On Bedrock access denied, returns a friendly fallback message. CORS enabled for dashboard origin. |

---

## Dashboard Features

| Feature | Implementation |
|---------|---------------|
| **Order list** | Fetches from `GET /api/orders`, displays status, destination, priority, Distance (km), ETA (min). Red blinking pulse when live telemetry + ETA are available. 5-second auto-refresh. |
| **Live delivery map** | Leaflet.js with CARTO dark tiles. Blue destination marker + green vehicle marker + dashed route polyline. Telemetry polled from `GET /api/test/telemetry/{orderId}` (Python service) every 5 seconds. `DeliveryMap` component with `key={selectedOrderId}` for stable React identity across polls. |
| **Logistics Assistant** | Floating chat bubble → dark modal. Select an order, ask context-aware questions. Calls `POST /api/assistant/chat`. Auto-scroll, selection-aware placeholder. |

---

## CI/CD & DevOps

### GitHub Actions

CI workflow (`.github/workflows/ci.yml`) triggers on push/PR to `main`:

| Job | Steps |
|-----|-------|
| **test-java-service** | JDK 21 (Temurin), `mvn clean test -B` |
| **test-python-service** | Python 3.10, `pip install -r requirements.txt`, `pytest -v` |

*Remaining:* Dashboard CI job (Vite build + Vitest) and Ruff lint step not yet added.

### Lambda Readiness (AI Service)

- **Mangum adapter** in `app.main.handler` wraps FastAPI for Lambda.
- **`Dockerfile.lambda`** uses `public.ecr.aws/lambda/python:3.10` base image, installs deps, sets handler to `app.main.handler`.
- Push to ECR and configure Lambda function to use the image.

### Local DevOps

- **Docker Compose:** PostgreSQL and DynamoDB Local for development.
- **Scripts:** `scripts/create-telemetry-table.ps1` (idempotent DynamoDB table creation), `scripts/aws-test.py` (Bedrock connectivity), movement simulator for telemetry.
- **Ports:** 8082 (Order), 5050 (AI), 9000 (DynamoDB), 5432 (PostgreSQL), 5173 (Vite). Windows: 5000–5035 often excluded; AI and config use 5050.

---

## Testing Strategy

| Service | Framework | Approach | Current Count |
|---------|-----------|----------|---------------|
| **Order Service (Java)** | JUnit 5, Mockito | Controller/Service/Repository unit tests; `MockRestServiceServer` for HTTP client tests; manual `CircuitBreakerRegistry` for CB tests (no full Spring context needed) | 19 tests |
| **AI Service (Python)** | Pytest | Engine unit tests (Haversine, ML model features); service tests with mocked DynamoDB/Bedrock/S3; API integration tests with `TestClient` | 17 tests |
| **Dashboard (TS)** | Vitest | Component rendering (basic). | 1 test |

TDD workflow: Red (failing test) → Green (minimal implementation) → Refactor. Moto / `unittest.mock` for AWS service mocking in Python; Mockito for Java.
