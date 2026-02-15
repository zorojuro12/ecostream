"""
EcoStream AI Forecasting Service
Main entry point for delay prediction and route analysis using GenAI.
"""
import logging
import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.api import assistant_routes, dev_routes, forecasting_routes

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="EcoStream AI Forecasting Service",
    description="Delay prediction and route analysis using GenAI",
    version="1.0.0"
)

# Allow dashboard (Vite default localhost:5173) to call this service
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# #region agent log – read body once for forecast POSTs so route receives it (body was consumed before route)
@app.middleware("http")
async def capture_forecast_body(request, call_next):
    if request.method == "POST" and request.url.path.startswith("/api/forecast/"):
        import json
        body_bytes = await request.body()
        request.state._forecast_body = body_bytes
        cl = request.headers.get("content-length")
        ct = request.headers.get("content-type", "")
        response = await call_next(request)
        try:
            _log_path = Path(__file__).parent.parent.parent.parent / ".cursor" / "debug.log"
            with open(_log_path, "a", encoding="utf-8") as _f:
                _f.write(json.dumps({"message": "forecast_request", "path": request.url.path, "content_length": cl, "body_captured_len": len(body_bytes), "response_status": response.status_code, "timestamp": __import__("time").time()}) + "\n")
        except Exception:
            pass
        return response
    return await call_next(request)
# #endregion


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    """Log 422 validation errors so we can see what the client sent vs what we expect."""
    import json
    print("[FORECAST 422] path=", request.url.path, "validation_errors=", exc.errors())
    logger.warning("Forecast 422: %s %s", request.url.path, exc.errors())
    # #region agent log
    try:
        _log_path = Path(__file__).parent.parent.parent.parent / ".cursor" / "debug.log"
        with open(_log_path, "a", encoding="utf-8") as _f:
            _f.write(json.dumps({"message": "forecast_422", "path": request.url.path, "validation_errors": exc.errors(), "timestamp": __import__("time").time()}) + "\n")
    except Exception:
        pass
    # #endregion
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


# Mount API routes
app.include_router(dev_routes.router)
app.include_router(forecasting_routes.router)
app.include_router(assistant_routes.router)


@app.get("/health")
async def health_check():
    """Health check endpoint to verify service is running."""
    return {"status": "healthy", "service": "ai-forecasting"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 5050))
    uvicorn.run(app, host="0.0.0.0", port=port)
