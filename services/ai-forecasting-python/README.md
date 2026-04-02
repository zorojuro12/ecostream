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

2. **Optional - Retrain the speed model** (a pre-trained `models/speed_model.joblib` is committed; retrain only if you want to update):
   ```bash
   # Download NYC Taxi Trip Duration train.csv from Kaggle → data/raw/train.csv
   python scripts/prepare_training_data.py   # clean + feature engineer → data/training_data.csv
   python scripts/train_model.py             # train RandomForest → models/speed_model.joblib
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

## AWS Lambda Deployment (SAM)

The service deploys to AWS Lambda as a container image via **SAM (Serverless Application Model)**. The SAM template provisions a Lambda function, HTTP API Gateway, and IAM policies for DynamoDB, S3, and Bedrock.

### Prerequisites
- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html) installed
- AWS CLI configured (`aws configure`) with a profile that has deploy permissions
- Docker running (SAM builds the container image locally)

### Quick deploy
```bash
cd services/ai-forecasting-python
./scripts/deploy-lambda.sh
```

### Step-by-step
```bash
cd services/ai-forecasting-python

# Build the container image
sam build

# Deploy (first time — creates ECR repo, CloudFormation stack, API Gateway)
sam deploy --guided
# Subsequent deploys (uses saved samconfig.toml defaults)
sam deploy
```

### Override parameters
```bash
sam deploy \
  --parameter-overrides \
    S3LogBucket=my-ecostream-logs \
    DynamoDbTableName=ecostream-telemetry \
    OrderServiceBaseUrl=https://orders.example.com
```

### What gets deployed
| Resource | Purpose |
|----------|---------|
| **Lambda function** | Container image (`Dockerfile.lambda`) with FastAPI + Mangum, ML model, and all deps |
| **HTTP API Gateway** | Routes all requests to the Lambda (catch-all `/{proxy+}`) with CORS |
| **IAM role** | DynamoDB read, S3 put (forecast logs), Bedrock invoke |

### Environment variables (set via SAM parameters or Lambda console)
| Variable | Default | Description |
|----------|---------|-------------|
| `EXECUTION_ENV` | `lambda` | Tells DynamoDB client to use real AWS (no endpoint override) |
| `DYNAMODB_TABLE_NAME` | `ecostream-telemetry-local` | DynamoDB table for telemetry reads |
| `S3_LOG_BUCKET` | *(empty)* | S3 bucket for forecast audit logs |
| `S3_LOG_PREFIX` | `delivery-logs/forecasts` | Key prefix for forecast log objects |
| `ORDER_SERVICE_BASE_URL` | *(empty)* | Order Service URL for assistant chat grounding |
| `CORS_ALLOWED_ORIGINS` | *(empty)* | Comma-separated origins; empty = localhost defaults |

### Building the Docker image manually
```bash
docker build -f Dockerfile.lambda -t ecostream-ai-lambda .
```
The image uses `public.ecr.aws/lambda/python:3.10`, installs deps, copies `app/` and `models/` (ML model artifact), and sets the handler to `app.main.handler`.

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

### Engine (ML + Haversine)
- [x] Haversine distance (`app/engine/forecaster.py`) - unit tested (SFU campuses ~13.72 km)
- [x] **Delivery speed prediction** (`app/engine/model_loader.py`): RandomForest pipeline trained on NYC Taxi Trip Duration data (Kaggle, 1.46M trips). Features: `distance_km`, `hour_of_day`, `day_of_week`, `month`, `priority`. Evaluation: MAE 4.24 km/h, RMSE 5.79 km/h, R² 0.45. Falls back to time-aware heuristic if model file missing.
- [x] Data pipeline: `scripts/prepare_training_data.py` (cleans raw CSV → `data/training_data.csv`, 20k rows)
- [x] Training script: `scripts/train_model.py` (train/test split, evaluate, save `models/speed_model.joblib`)

### Services
- [x] DynamoDB Telemetry Reader (`app/services/telemetry_service.py`) - endpoint http://localhost:9000, `get_latest_telemetry(order_id)`
- [x] Forecasting Service (`app/services/forecasting_service.py`): `calculate_eta(order_id, destination, priority)` - uses Haversine + ML speed; **logs every successful forecast to S3** via `upload_forecast_log()` (fire-and-forget; no-op when `S3_LOG_BUCKET` is unset)
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
- [x] `tests/unit/test_ml_engine.py` - multi-feature speed prediction (Express vs Standard, rush-hour vs off-peak, model vs fallback)
- [x] `tests/test_bedrock_client.py` - Bedrock Converse client (converse called, fallback on AccessDenied)
- [x] `tests/test_assistant_service.py` - assistant chat with mocked ETA and get_ai_insight (data grounding)
- [x] `tests/test_assistant_api.py` - POST /api/assistant/chat returns real reply when Bedrock mocked (not fallback)
- [x] `tests/test_s3_logger.py` - S3 logger wiring (upload called on successful ETA, skipped on no telemetry, skipped when bucket unset)

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
# Expected: Application startup on port 5050

# Option C: Uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 5050 --reload
# Expected: Uvicorn running on http://0.0.0.0:5050
```

### Health Check
```bash
# Test health endpoint (PowerShell)
curl.exe http://localhost:5050/health
# Expected: {"status":"healthy","service":"ai-forecasting"}

# Alternative (PowerShell)
Invoke-RestMethod -Uri http://localhost:5050/health
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
- `/app/engine`: ML/forecasting - `forecaster.py` (Haversine), `model_loader.py` (speed prediction), `bedrock_client.py` (Bedrock Converse, us-east-1)
- `/app/api`: Routes and schemas - `forecasting_routes.py`, `dev_routes.py`, `assistant_routes.py`, `schemas.py`
- `/app/services`: Business logic and DynamoDB - `telemetry_service.py`, `forecasting_service.py`, `assistant_service.py`
- `/scripts`: `prepare_training_data.py` (raw CSV → features), `train_model.py` (train + evaluate → `.joblib`)
- `/data`: `training_data.csv` (20k processed rows, committed); `raw/` (source CSVs, gitignored)
- `/models`: `speed_model.joblib` (trained RandomForest pipeline, committed)
- `/tests/unit`: `test_forecaster.py`, `test_ml_engine.py`
- `/tests`: `test_bedrock_client.py`, `test_assistant_service.py`, `test_forecast_api.py`
