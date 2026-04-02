"""
Forecasting API routes — ETA calculation endpoints.
"""
from fastapi import APIRouter, HTTPException, status

from app.api.schemas import ForecastRequest, ForecastResponse
from app.services.forecasting_service import calculate_eta

router = APIRouter(prefix="/api/forecast", tags=["forecasting"])


@router.post("/{order_id}", response_model=ForecastResponse)
async def forecast_eta(order_id: str, request: ForecastRequest):
    """Calculate Estimated Time of Arrival for an order."""
    result = calculate_eta(
        order_id=order_id,
        destination_latitude=request.destination_latitude,
        destination_longitude=request.destination_longitude,
        priority=request.priority,
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No telemetry data found for order ID: {order_id}",
        )

    return ForecastResponse(
        distance_km=result["distance_km"],
        estimated_arrival_minutes=result["estimated_arrival_minutes"],
    )
