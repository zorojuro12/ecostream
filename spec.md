# EcoStream Technical Specification

## System Overview

EcoStream is a **serverless-ready, polyglot microservices platform** utilizing **GenAI for logistics optimization**. It delivers last-mile delivery optimization by combining real-time telemetry, ML-based ETA forecasting, and a context-aware Logistics Assistant (Claude via Amazon Bedrock). The system is implemented for local development today with a clear path to AWS cloud deployment.

---

## Architecture Map

### Current Local Setup

| Component | Technology | Port | Responsibility |
|-----------|------------|------|----------------|
| **Order Service** | Java 21, Spring Boot 3.4 | **8082** | CRUD for orders (PostgreSQL), telemetry ingestion (DynamoDB), orchestration; enriches GET order with ETA from AI service. |
| **AI Forecasting Service** | Python 3.x, FastAPI | **5050** | ETA (Haversine + Scikit-Learn), `POST /api/forecast/{order_id}`; Logistics Assistant `POST /api/assistant/chat` (Bedrock Converse API, Claude 3.5 Haiku, us-east-1). |
| **PostgreSQL** | Docker | 5432 | Order persistence (Single Source of Truth for order and destination). |
| **DynamoDB Local** | Docker | **9000** (external) | Telemetry table `ecostream-telemetry-local` (partition: orderId, sort: timestamp). |
| **Dashboard** | TypeScript, React, Vite, Tailwind | **5173** (Vite dev) | Order list with Distance/ETA, live-tracking indicator, floating Logistics Assistant chat. |

- **Order Service** calls AI service at `ai.forecasting.base-url` (default `http://localhost:5050`) for forecast and uses DynamoDB at `http://localhost:9000`.
- **Dashboard** calls Order Service at `http://localhost:8082` and AI service at `http://localhost:5050` for the assistant chat (CORS enabled for localhost:5173).

### Target Cloud Architecture

| AWS Service | Purpose |
|-------------|---------|
| **API Gateway** | Single entry point for orders, telemetry, and (optionally) assistant; rate limiting and auth. |
| **AWS Lambda** | Python AI service (forecast + assistant) as serverless functions; event-driven scaling. |
| **Amazon RDS (PostgreSQL)** | Managed Order persistence; same schema as local. |
| **Amazon DynamoDB** | Managed telemetry table; same key schema (orderId PK, timestamp SK). |
| **Amazon S3** | Logs, training data for ML models, and static assets if needed. |
| **Amazon Bedrock** | Already used for Logistics Assistant (Converse API, Claude 3.5 Haiku, us-east-1). |
| **CloudWatch** | Logs, metrics, and alarms for all services. |

- Migration path: Order Service can remain on ECS/EC2 or move to Lambda/container; AI service is a natural Lambda candidate. Dashboard can be hosted on S3 + CloudFront.

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

**API response (OrderResponseDTO)** also includes enriched fields when AI is available: `destination` (lat/lon), `priority`, `distanceKm`, `estimatedArrivalMinutes` (null if AI unavailable).

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

## Integration Contracts (APIs)

### Order Service (Java) – base URL local: `http://localhost:8082`

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/orders` | List all orders. |
| `GET` | `/api/orders/{id}` | Get order by ID. **Enriched** with `distanceKm` and `estimatedArrivalMinutes` from AI service (POST /api/forecast/{order_id}). 404 if not found. |
| `POST` | `/api/orders` | Create order (body: destination, priority, etc.). Returns 201 with order. |
| `PUT` | `/api/orders/{id}` | Update order (partial). |
| `DELETE` | `/api/orders/{id}` | Delete order. 204 on success. |
| `POST` | `/api/orders/{id}/telemetry` | Ingest telemetry. Body: `{ "latitude", "longitude" }` (current position). Order Service generates timestamp and writes to DynamoDB. 202 Accepted. |

### AI Forecasting Service (Python) – base URL local: `http://localhost:5050`

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check. |
| `POST` | `/api/forecast/{order_id}` | **ETA forecast.** Body: `destination_latitude`, `destination_longitude`, `priority` (optional, default "Standard"). Returns `{ "distance_km", "estimated_arrival_minutes" }`. 404 if no telemetry for order. Called by Order Service when enriching GET /api/orders/{id}. |
| `POST` | `/api/assistant/chat` | **Logistics Assistant (GenAI).** Body: `order_id`, `message`. AI service fetches order from Order Service (SSoT), computes distance/ETA from telemetry + Haversine, injects context into system prompt, and calls **Bedrock Converse API** (Claude 3.5 Haiku, us-east-1). Returns `{ "reply": "..." }`. On Bedrock access denied, returns a friendly fallback message. CORS enabled for dashboard origin (e.g. localhost:5173). |

- The deprecated `POST /predict/delay` endpoint is **removed**; ETA is provided by `POST /api/forecast/{order_id}` and the assistant uses the same data source.

---

## CI/CD & DevOps

### GitHub Actions (Planned)

- **Workflows:** Automated testing on push/PR for:
  - **Order Service:** Maven build and unit tests (JUnit 5, Mockito).
  - **AI Service:** Pytest (unit + API tests), Ruff lint/format.
  - **Dashboard:** Vitest, build (Vite).
- **Deployment strategy:** Build and test on main/develop; deploy to AWS (e.g. Lambda for AI, ECS or Lambda for Order Service, S3/CloudFront for dashboard) via GitHub Actions with AWS credentials (OIDC or secrets). CloudWatch for logs and metrics.
- **Artifacts:** JAR (Order Service), Python package or Lambda bundle (AI Service), static bundle (Dashboard) produced by CI for deployment.

### Local DevOps

- **Docker Compose:** PostgreSQL and DynamoDB Local for development.
- **Scripts:** `scripts/create-telemetry-table.ps1` (idempotent DynamoDB table creation), `scripts/aws-test.py` (Bedrock connectivity), movement simulator for telemetry.
- **Ports:** 8082 (Order), 5050 (AI), 9000 (DynamoDB), 5173 (Vite). Windows: 5000–5035 often excluded; AI and config use 5050.
