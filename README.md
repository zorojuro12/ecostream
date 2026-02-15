# EcoStream

[![CI](https://github.com/Your-Username/ecostream/actions/workflows/ci.yml/badge.svg)](https://github.com/Your-Username/ecostream/actions/workflows/ci.yml)

**A serverless-ready, polyglot microservices platform utilizing GenAI for logistics optimization.**

EcoStream combines real-time delivery telemetry, ML-based ETA forecasting, and a context-aware **Logistics Assistant** (Claude via Amazon Bedrock) to optimize last-mile delivery. Built with Java (Order Service), Python (AI Service), and a TypeScript/React dashboard—running locally today with a clear path to AWS.

---

## What's in the repo

| Service | Stack | Port | Role |
|--------|--------|------|------|
| **Order Service** | Java 21, Spring Boot | **8082** | CRUD + telemetry ingestion; enriches orders with ETA from the AI service. |
| **AI Forecasting Service** | Python, FastAPI | **5050** | ETA (Haversine + Scikit-Learn), **Logistics Assistant** chat (Bedrock, Claude 3.5 Haiku). |
| **Dashboard** | TypeScript, React, Vite, Tailwind | **5173** | Order list with Distance/ETA, live-tracking indicator, floating assistant chat. |
| **PostgreSQL** | Docker | 5432 | Order persistence. |
| **DynamoDB Local** | Docker | **9000** | Real-time telemetry (orderId + timestamp). |

- **Single Source of Truth:** The Order Service owns order and destination data; the AI service and dashboard consume it via APIs.
- **Technical spec:** See [spec.md](spec.md) for architecture, data models, API contracts, and target cloud (API Gateway, Lambda, RDS, DynamoDB, S3, CloudWatch).

---

## Quick start (local)

**Prerequisites:** Java 21, Maven, Python 3.9+, Node.js, Docker.

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
   Runs on **8082**.

4. **AI Service** (optional: add AWS credentials to `services/ai-forecasting-python/.env` for the assistant)
   ```bash
   cd services/ai-forecasting-python && pip install -r requirements.txt && uvicorn app.main:app --host 0.0.0.0 --port 5050
   ```
   Runs on **5050**.

5. **Dashboard**
   ```bash
   cd services/web-dashboard-ts && npm install && npm run dev
   ```
   Open **http://localhost:5173**. Select an order, open the floating chat, and ask the Logistics Assistant (e.g. *"What is my current ETA?"*).

6. **Simulate movement** (optional)
   ```bash
   python scripts/simulate_movement.py <order-id>
   ```
   Use an order ID from the dashboard or from `GET http://localhost:8082/api/orders`.

---

## Features

- **Order CRUD & telemetry:** Create orders, ingest live coordinates via `POST /api/orders/{id}/telemetry`; data stored in PostgreSQL (orders) and DynamoDB (telemetry).
- **ETA forecasting:** Order Service calls the AI service to enrich `GET /api/orders/{id}` with distance and estimated arrival time (Haversine + priority-based speed).
- **Logistics Assistant:** Dashboard chat sends questions to `POST /api/assistant/chat`. The AI service fetches order context from the Order Service, computes live distance/ETA, and calls **Amazon Bedrock** (Converse API, Claude 3.5 Haiku, us-east-1) for grounded replies.
- **Real-time UI:** Auto-refresh, live-tracking pulse, and selection-aware assistant chat.

---

## Documentation

- **[spec.md](spec.md)** — Technical specification: local vs target cloud architecture, data models, API contracts, CI/CD.
- **Service READMEs** — Per-service setup and APIs:
  - [services/order-service-java/README.md](services/order-service-java/README.md)
  - [services/ai-forecasting-python/README.md](services/ai-forecasting-python/README.md)
  - [services/web-dashboard-ts/README.md](services/web-dashboard-ts/README.md)
- **[progress.md](progress.md)** — Implementation progress and verification notes.

---

## Tech stack

| Layer | Technologies |
|-------|----------------|
| **Backend** | Java 21 (Spring Boot), Python (FastAPI) |
| **Frontend** | TypeScript, React, Vite, Tailwind |
| **Data** | PostgreSQL (orders), DynamoDB (telemetry) |
| **AI/ML** | Amazon Bedrock (Claude 3.5 Haiku), Scikit-Learn |
| **DevOps** | Docker, Docker Compose; GitHub Actions (CI on push/PR to main) |

---

## License

See [LICENSE](LICENSE) if present.
