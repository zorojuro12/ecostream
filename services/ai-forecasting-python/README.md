# AI Forecasting Service

## Service Purpose
The AI Forecasting Service provides delay prediction and route analysis capabilities using machine learning (Scikit-Learn) and GenAI (Amazon Bedrock). It processes order details and returns estimated delay predictions to help optimize last-mile delivery operations.

## Tech Stack
- **Framework:** FastAPI 0.115.0
- **Language:** Python 3.x
- **ML Library:** Scikit-Learn (for delay prediction models)
- **GenAI Integration:** Amazon Bedrock (Logistics Assistant)
- **Validation:** Pydantic 2.10.0
- **Linting/Formatting:** Ruff 0.8.0
- **Testing:** Pytest

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

2. **Run the Service:**
   
   **Option A - Using PowerShell script (Windows):**
   ```powershell
   .\start-ai-service.ps1
   ```
   This script automatically checks Python, activates virtual environment, installs dependencies, and starts the service.

   **Option B - Manual start:**
   ```bash
   python -m app.main
   ```

   **Option C - Using uvicorn directly:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
   ```

   The service will start on port **5000** (default, configurable via `PORT` environment variable).

3. **Verify Health:**
   ```bash
   curl http://localhost:5000/health
   ```

## Current State

### Infrastructure
- ✅ FastAPI application skeleton initialized
- ✅ Health check endpoint (`/health`) implemented
- ✅ Dependencies configured (FastAPI, Uvicorn, Pydantic, Ruff, python-dotenv)
- ✅ Project structure created (`/app/engine`, `/app/api`, `/app/services`, `/app/schemas`)
- ✅ Main application moved to `/app/main.py` with `.env` loading
- ✅ Port configuration via environment variable (default: 5000)
- ✅ PowerShell startup script (`start-ai-service.ps1`) for Windows convenience

### Data Models & Validation
- ✅ Location schema (`app/api/schemas.py`) with Java parity validation:
  - Latitude: -90.0 to 90.0 (inclusive)
  - Longitude: -180.0 to 180.0 (inclusive)

### Pending Implementation
- ⏳ DynamoDB Telemetry Reader service (boto3 integration)
- ⏳ ETA calculation logic (Distance/Time)
- ⏳ Scikit-Learn delay prediction model setup
- ⏳ `/predict/delay` endpoint implementation
- ⏳ Amazon Bedrock integration for route analysis
- ⏳ Unit tests using Pytest

## Verified Commands

### Tool Verification
```bash
# Verify Python 3.9+ is installed
python --version
# Expected: Python 3.9.x or higher

# Verify pip is available
pip --version
# Expected: pip version information
```

### Dependency Management
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

# Run tests (when implemented)
pytest
```

## API Contract

### Endpoints (Planned)
- `POST http://localhost:5000/predict/delay`: Accepts order details, returns estimated delay in minutes
  - **Request Body:** Order details (destination, priority, etc.)
  - **Response:** `{ "estimatedDelayMinutes": int }`

## Code Organization
Following the FastAPI standards, the service will be organized as:
- `/engine`: Machine learning models and prediction logic
- `/api`: API route handlers and endpoints
- `/schemas`: Pydantic models for request/response validation
