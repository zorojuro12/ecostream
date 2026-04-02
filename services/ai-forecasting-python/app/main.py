"""
EcoStream AI Forecasting Service — main entry point.
"""
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from mangum import Mangum
from app.api import assistant_routes, dev_routes, forecasting_routes
from app.utils.logging_config import configure_logging

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

configure_logging()
logger = logging.getLogger(__name__)

_DEFAULT_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]


def _allowed_origins() -> list[str]:
    """Build CORS allow-origins list from env, falling back to localhost dev defaults."""
    extra = os.getenv("CORS_ALLOWED_ORIGINS", "")
    origins = [o.strip() for o in extra.split(",") if o.strip()] if extra else []
    return origins or _DEFAULT_ORIGINS


app = FastAPI(
    title="EcoStream AI Forecasting Service",
    description="Delay prediction and route analysis using GenAI",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(dev_routes.router)
app.include_router(forecasting_routes.router)
app.include_router(assistant_routes.router)


@app.get("/health")
async def health_check():
    """Health check endpoint to verify service is running."""
    return {"status": "healthy", "service": "ai-forecasting"}


handler = Mangum(app)


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 5050))
    uvicorn.run(app, host="0.0.0.0", port=port)
