# EcoStream

[![CI](https://github.com/Your-Username/ecostream/actions/workflows/ci.yml/badge.svg)](https://github.com/Your-Username/ecostream/actions/workflows/ci.yml)

**A serverless-ready, polyglot microservices platform utilizing GenAI for logistics optimization.**

EcoStream combines real-time delivery telemetry, ML-based ETA forecasting, and a context-aware **Logistics Assistant** (Claude via Amazon Bedrock) to optimize last-mile delivery. Built with Java (Order Service), Python (AI Service), and a TypeScript/React dashboard — running locally today with a clear path to AWS.

---

## What's in the repo

| Service | Stack | Port | Role |
|---------|-------|------|------|
| **Order Service** | Java 21, Spring Boot 3.4 | **8082** | CRUD + telemetry ingestion (DynamoDB); enriches orders with ETA from AI service. Resilience4j circuit breaker on AI client; Actuator health/CB-state endpoints. Environment-aware DB config for RDS migration. |
| **AI Forecasting Service** | Python 3.x, FastAPI | **5050** | ETA via Haversine + RandomForest ML model (trained on NYC Taxi data); Logistics Assistant chat (Bedrock, Claude 3.5 Haiku); S3 forecast logging; structured JSON logging. Lambda-ready (SAM + Mangum + Docker). |
| **Dashboard** | TypeScript, React, Vite, Tailwind | **5173** | Order list with Distance/ETA and live-tracking pulse; **live delivery map** (Leaflet.js, CARTO dark tiles, vehicle/destination markers, route polyline); floating Logistics Assistant chat. |
| **PostgreSQL** | Docker | 5432 | Order persistence. |
| **DynamoDB Local** | Docker | **9000** | Real-time telemetry (orderId + timestamp). |

- **Single Source of Truth:** The Order Service owns order and destination data; the AI service and dashboard consume it via APIs.
- **Technical spec:** See [spec.md](spec.md) for architecture, data models, API contracts, and target cloud (API Gateway, Lambda, RDS, DynamoDB, S3, Bedrock, CloudWatch).

---

## Quick start (local)

**Prerequisites:** Java 21, Maven, Python 3.9+, Node.js 20+, Docker.

1. **Clone and start infrastructure**
   ```bash
   git clone https://github.com/Your-Username/ecostream.git
   cd ecostream
   docker-compose up -d postgres dynamodb-local
   ```

2. **Create DynamoDB telemetry table** (one-time)
   ```powershell
   .\scripts\create-telemetry-table.ps1
   ```

3. **Order Service** (from repo root)
   ```bash
   cd services/order-service-java && mvn spring-boot:run
   ```
   Runs on **8082**. Health: `GET http://localhost:8082/actuator/health`

4. **AI Service** (optional: add AWS credentials to `services/ai-forecasting-python/.env` for the Bedrock-backed assistant)
   ```bash
   cd services/ai-forecasting-python
   pip install -r requirements.txt
   uvicorn app.main:app --host 0.0.0.0 --port 5050
   ```
   Runs on **5050**. Health: `GET http://localhost:5050/health`

5. **Dashboard**
   ```bash
   cd services/web-dashboard-ts && npm install && npm run dev
   ```
   Open **http://localhost:5173**. Select an order, view the live map, and open the floating chat to ask the Logistics Assistant (e.g. *"What is my current ETA?"*).

6. **Simulate movement** (optional — feeds telemetry for the live map)
   ```bash
   python scripts/simulate_movement.py <order-id>
   ```

---

## Features

- **Order CRUD & telemetry:** Create orders, ingest live coordinates via `POST /api/orders/{id}/telemetry`; data stored in PostgreSQL (orders) and DynamoDB (telemetry).
- **ML-powered ETA forecasting:** RandomForest model trained on NYC Taxi Trip Duration data (Kaggle, 1.46M trips). Predicts delivery speed from distance, time-of-day, day-of-week, month, and priority. ETA = distance / predicted speed. Heuristic fallback when model file is absent.
- **Logistics Assistant (GenAI):** Dashboard chat sends questions to `POST /api/assistant/chat`. The AI service fetches order context, computes live distance/ETA, and calls **Amazon Bedrock** (Converse API, Claude 3.5 Haiku, us-east-1) for grounded replies. Fallback message on access denied.
- **Live delivery map:** Leaflet.js with CARTO dark tiles — vehicle marker, destination marker, dashed route polyline. Telemetry polled every 5 seconds from the AI service.
- **Resilience:** Resilience4j circuit breaker on the Order → AI service call. Graceful degradation: orders are served without ETA when the AI service is down. Spring Boot Actuator exposes health, info, and circuit breaker state.
- **S3 forecast logging:** Every successful ETA computation is durably logged to S3 as JSON (fire-and-forget; no-op when `S3_LOG_BUCKET` is unset).
- **Structured JSON logging:** All Python service logs output as single-line JSON (`timestamp`, `level`, `logger`, `message`) for CloudWatch / log aggregators. `LOG_LEVEL` configurable via env.
- **Real-time UI:** Auto-refresh (5s), live-tracking pulse indicator, selection-aware assistant chat.

---

## Documentation

- **[spec.md](spec.md)** — Technical specification: local vs target cloud architecture, data models, API contracts, resilience, ML/AI, CI/CD.
- **Service READMEs** — Per-service setup, APIs, and current capabilities:
  - [services/order-service-java/README.md](services/order-service-java/README.md)
  - [services/ai-forecasting-python/README.md](services/ai-forecasting-python/README.md)
  - [services/web-dashboard-ts/README.md](services/web-dashboard-ts/README.md)
- **[progress.md](progress.md)** — Implementation progress and verification notes.

---

## Tech stack

| Layer | Technologies |
|-------|-------------|
| **Backend** | Java 21 (Spring Boot 3.4, Resilience4j, Actuator), Python (FastAPI, Mangum) |
| **Frontend** | TypeScript, React 19, Vite, Tailwind, Leaflet.js |
| **Data** | PostgreSQL (orders), DynamoDB (telemetry), S3 (forecast logs) |
| **AI/ML** | Amazon Bedrock (Claude 3.5 Haiku), Scikit-Learn (RandomForest) |
| **Infrastructure** | Docker, Docker Compose, AWS SAM (Lambda + API Gateway) |
| **CI/CD** | GitHub Actions (3 jobs: Java, Python, Dashboard) |
| **Testing** | JUnit 5, Mockito (Java); Pytest (Python); Vitest, Testing Library (Dashboard) |

---

## CI/CD & Deployment

### GitHub Actions

CI workflow (`.github/workflows/ci.yml`) triggers on push/PR to `main`:

| Job | Steps |
|-----|-------|
| **test-java-service** | JDK 21 (Temurin), `mvn clean test -B` |
| **test-python-service** | Python 3.10, `pip install -r requirements.txt`, `pytest -v` |
| **test-dashboard** | Node.js 20, `npm ci`, `tsc -b && vite build`, `vitest run` |

### Lambda Deployment (AI Service)

The AI service deploys to AWS Lambda as a container image via **SAM**:

```bash
cd services/ai-forecasting-python
sam build
sam deploy --guided   # first time
sam deploy            # subsequent (uses samconfig.toml defaults)
```

Or use the one-command script: `./scripts/deploy-lambda.sh`

**What gets deployed:** Lambda function (container image with FastAPI + ML model), HTTP API Gateway (catch-all proxy with CORS), IAM role (DynamoDB read, S3 put, Bedrock invoke).

See [services/ai-forecasting-python/README.md](services/ai-forecasting-python/README.md) for full deployment docs.

---

## Testing

| Service | Framework | Count | Approach |
|---------|-----------|-------|----------|
| **Order Service (Java)** | JUnit 5, Mockito | 19 | Controller, Service, Repository unit tests; `MockRestServiceServer` for HTTP client; manual `CircuitBreakerRegistry` for circuit breaker tests |
| **AI Service (Python)** | Pytest | 19 | Haversine, ML model, Bedrock client, assistant service, forecast API, S3 logger, JSON log formatter — all with mocked AWS services |
| **Dashboard (TS)** | Vitest, Testing Library | 13 | OrderList (rendering, selection, empty state, live pulse), AssistantChat (open/close, send/receive, error), API clients |

TDD workflow: Red (failing test) → Green (minimal implementation) → Refactor.

---

## License

See [LICENSE](LICENSE) if present.
