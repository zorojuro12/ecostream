"""
EcoStream AI Forecasting Service
Main entry point for delay prediction and route analysis using GenAI.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

app = FastAPI(
    title="EcoStream AI Forecasting Service",
    description="Delay prediction and route analysis using GenAI",
    version="1.0.0"
)


@app.get("/health")
async def health_check():
    """Health check endpoint to verify service is running."""
    return {"status": "healthy", "service": "ai-forecasting"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 5000))
    uvicorn.run(app, host="0.0.0.0", port=port)
