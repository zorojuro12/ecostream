# AI Forecasting Service

## Service Purpose
The AI Forecasting Service provides delay prediction, route analysis, and the **Logistics Assistant** for EcoStream. It uses Scikit-Learn for priority-based speed prediction and ETA calculation. The Java Order Service calls this service when fetching an order to enrich responses with `distance_km` and `estimated_arrival_minutes`. The **Logistics Assistant** uses Amazon Bedrock (Converse API, Claude 3.5 Haiku, us-east-1) with data grounding (distance + ETA) via `POST /api/assistant/chat`.

## Tech Stack
- **Framework:** FastAPI 0.115.0
- **Language:** Python 3.x
- **ML Library:** Scikit-Learn (for delay prediction models)
- **GenAI Integration:** Amazon Bedrock (Logistics Assistant)
- **Validation:** Pydantic 2.10.0
- **Linting/Formatting:** Ruff 0.8.0
- **Testing:** Pytest 9.0.2
- **AWS SDK:** boto3 1.34.0 (DynamoDB)

## Local Setup

### Prerequisites
- Python 3.9+
- pip

### Running the Service

1. **Install Dependencies:**
   ```bash
   cd services/ai-forecasting-python
   pip install -r requirements.txt
   ```

2. **Optional - Train the speed model** (if `models/speed_model.joblib` is missing, the service falls back to hardcoded Express=60 km/h, Standard=30 km/h):
   ```bash
   python scripts/train_mock_model.py
   ```

3. **Run the Service:**

   **Option A - Using PowerShell script (Windows):**
   ```powershell
   .\start-ai-service.ps1
   ```

   **Option B - Manual start:**
   ```bash
   python -m app.main
   ```

   **Option C - Using uvicorn directly:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 5050 --reload
   ```

   The service runs on port **5050** by default (Windows often excludes 5000–5035 — WSAEACCES 10013). Override with `$env:PORT` (PowerShell) or `PORT=5050` (bash) if needed.

4. **Verify Health:**
   ```bash
   curl http://localhost:5050/health
   ```

## Building the Lambda Docker image

The service is Lambda-ready via [Mangum](https://mangum.io/) and a dedicated Dockerfile. To build the image used for AWS Lambda (or Lambda-style container deployment):

```bash
cd services/ai-forecasting-python
docker build -f Dockerfile.lambda -t ecostream-ai-lambda .
```

The image uses the AWS base image `public.ecr.aws/lambda/python:3.10`, installs dependencies from `requirements.txt`, copies the `app` directory, and sets the Lambda handler to `app.main.handler` (the Mangum-wrapped FastAPI app). Push this image to ECR and configure your Lambda function to use it.

## Current Capabilities

### Infrastructure
- [x] FastAPI application with `/app` structure
- [x] Health check: `GET /health`
- [x] Port 5050 default (5000–5035 often excluded on Windows), configurable via PORT env
- [x] Dependencies: FastAPI, Uvicorn, Pydantic, Ruff, python-dotenv, boto3, scikit-learn, joblib, pytest

### Data Models & Validation
- [x] Location schema with Java parity: latitude [-90, 90], longitude [-180, 180]
- [x] ForecastRequest: destination coordinates + optional `priority` (Express / Standard)
- [x] ForecastResponse: `distance_km`, `estimated_arrival_minutes`

### Engine (Pure ML, No I/O)
- [x] Haversine distance (`app/engine/forecaster.py`) - unit tested (SFU campuses ~13.72 km)
- [x] Priority-based speed prediction (`app/engine/model_loader.py`): loads `models/speed_model.joblib` or falls back to Express=60 km/h, Standard=30 km/h
- [x] Training script: `scripts/train_mock_model.py` produces a Scikit-Learn pipeline saved as `.joblib`

### Services
- [x] DynamoDB Telemetry Reader (`app/services/telemetry_service.py`) - endpoint http://localhost:9000, `get_latest_telemetry(order_id)`
- [x] Forecasting Service (`app/services/forecasting_service.py`): `calculate_eta(order_id, destination, priority)` - uses Haversine + ML speed
- [x] **Logistics Assistant** (`app/services/assistant_service.py`): grounds user questions with live distance/ETA, then calls Bedrock; identity + context in XML (`<context>Distance: Xkm, ETA: Ymin</context>`)

### API Endpoints
- [x] `GET /health`
- [x] `GET /api/test/telemetry/{order_id}`
- [x] `POST /api/forecast/{order_id}` - body: `destination_latitude`, `destination_longitude`, optional `priority` (default "Standard")
- [x] `POST /api/assistant/chat` - Logistics Assistant: body `order_id`, `message`, `destination_latitude`, `destination_longitude`, `priority`; returns `reply` (Bedrock response or fallback)
- [x] **Verified:** End-to-end with Order Service — Java client sends JSON body (snake_case); dashboard shows distance_km, estimated_arrival_minutes, and live-tracking indicator when simulation runs for an order
- [x] **Verified:** Logistics Assistant returns real Claude replies when `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` are set in service `.env`; `get_bedrock_client()` loads .env (service dir + repo root) so the running app uses the same credentials as `scripts/aws-test.py`

### Testing
- [x] `tests/unit/test_forecaster.py` - Haversine
- [x] `tests/unit/test_ml_engine.py` - priority-based speed and travel time (mocked and real model)
- [x] `tests/test_bedrock_client.py` - Bedrock Converse client (converse called, fallback on AccessDenied)
- [x] `tests/test_assistant_service.py` - assistant chat with mocked ETA and get_ai_insight (data grounding)
- [x] `tests/test_assistant_api.py` - POST /api/assistant/chat returns real reply when Bedrock mocked (not fallback)

### Pending
- [ ] Additional integration tests if needed

## Verified Commands

```bash
# Lint and format
ruff check . --fix
ruff format .

# Tests
pytest tests/unit/ -v
pytest tests/unit/test_forecaster.py tests/unit/test_ml_engine.py -v
pytest tests/test_bedrock_client.py tests/test_assistant_service.py tests/test_forecast_api.py -v
```

**Test Logistics Assistant** (service on 5050; use an order_id that has telemetry):
```bash
# Navigate to service directory
cd services/ai-forecasting-python

# Install dependencies (global)
pip install -r requirements.txt

# Or use virtual environment (recommended)
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Verify key dependencies
pip list | findstr "fastapi uvicorn pydantic scikit-learn boto3"
# Expected: All packages listed with versions
```

### Run Service
```bash
# Option A: PowerShell script (Windows - recommended)
.\start-ai-service.ps1
# Automatically: checks Python, creates venv, installs deps, starts service

# Option B: Manual start
python -m app.main
# Expected: Application startup on port 5000

# Option C: Uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
# Expected: Uvicorn running on http://0.0.0.0:5000
```

### Health Check
```bash
# Test health endpoint (PowerShell)
curl.exe http://localhost:5000/health
# Expected: {"status":"healthy","service":"ai-forecasting"}

# Alternative (PowerShell)
Invoke-RestMethod -Uri http://localhost:5000/health
# Expected: status=healthy, service=ai-forecasting
```

### Development Tools
```bash
# Run Ruff linter
ruff check .

# Format code with Ruff
ruff format .

# Run unit tests
pytest tests/unit/

# Run all tests with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_forecaster.py -v
```

## API Contract

### GET /health
- **Response:** `{ "status": "healthy", "service": "ai-forecasting" }`

### GET /api/test/telemetry/{order_id}
- **Path:** `order_id` (string)
- **Response:** `{ "latitude": float, "longitude": float }` or 404

### POST /api/forecast/{order_id}
- **Path:** `order_id` (string)
- **Request Body:**
  ```json
  {
    "destination_latitude": 49.2820,
    "destination_longitude": -123.1085,
    "priority": "Standard"
  }
  ```
  `priority` is optional; "Express" gives faster predicted speed than "Standard".
- **Response:**
  ```json
  {
    "distance_km": 13.83,
    "estimated_arrival_minutes": 20.7
  }
  ```
- **Errors:** 404 if no telemetry for the order

### POST /api/assistant/chat (Logistics Assistant)
- **Request Body:**
  ```json
  {
    "order_id": "uuid-with-telemetry",
    "message": "Based on my current speed, why am I delayed?",
    "destination_latitude": 49.28,
    "destination_longitude": -123.12,
    "priority": "Standard"
  }
  ```
- **Response:** `{ "reply": "string" }` — Bedrock answer grounded with distance/ETA, or fallback message if Bedrock access is denied.
- **Region:** Bedrock client uses `us-east-1`. Model: `us.anthropic.claude-3-5-haiku-20241022-v1:0`.

## Code Organization
- `/app/engine`: Pure ML/forecasting (no I/O) - `forecaster.py`, `model_loader.py`, `bedrock_client.py` (Bedrock Converse, us-east-1)
- `/app/api`: Routes and schemas - `forecasting_routes.py`, `dev_routes.py`, `assistant_routes.py`, `schemas.py`
- `/app/services`: Business logic and DynamoDB - `telemetry_service.py`, `forecasting_service.py`, `assistant_service.py`
- `/scripts`: `train_mock_model.py` - trains and saves `models/speed_model.joblib`
- `/tests/unit`: `test_forecaster.py`, `test_ml_engine.py`
- `/tests`: `test_bedrock_client.py`, `test_assistant_service.py`, `test_forecast_api.py`
