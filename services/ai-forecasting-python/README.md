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
   ```bash
   python main.py
   ```

   Or using uvicorn directly:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 5000
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
- ✅ Dependencies configured (FastAPI, Uvicorn, Pydantic, Ruff)
- ✅ Project structure created (`/app/engine`, `/app/api`, `/app/schemas`)
- ✅ Port configuration via environment variable (default: 5000)

### Pending Implementation
- ⏳ Scikit-Learn delay prediction model setup
- ⏳ `/predict/delay` endpoint implementation
- ⏳ Pydantic request/response schemas for delay prediction
- ⏳ Amazon Bedrock integration for route analysis
- ⏳ Populate project structure directories with actual implementation
- ⏳ Unit tests using Pytest

## API Contract

### Endpoints (Planned)
- `POST /predict/delay`: Accepts order details, returns estimated delay in minutes
  - **Request Body:** Order details (destination, priority, etc.)
  - **Response:** `{ "estimatedDelayMinutes": int }`

## Code Organization
Following the FastAPI standards, the service will be organized as:
- `/engine`: Machine learning models and prediction logic
- `/api`: API route handlers and endpoints
- `/schemas`: Pydantic models for request/response validation
