"""
Forecasting API routes.
Exposes endpoints for ETA calculation and delay prediction.
"""
import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request, status

from app.api.schemas import ForecastRequest, ForecastResponse
from app.services.forecasting_service import calculate_eta

router = APIRouter(prefix="/api/forecast", tags=["forecasting"])


@router.post("/{order_id}", response_model=ForecastResponse)
async def forecast_eta(order_id: str, request: Request):
    """
    Calculate Estimated Time of Arrival (ETA) for an order.

    Uses ML-predicted speed from request priority (Express = faster, Standard = slower).
    Reads body explicitly so the stream is not consumed before parsing (fixes 422 when body arrives with Content-Length set).
    """
    body_bytes = getattr(request.state, "_forecast_body", None) or await request.body()
    # #region agent log – body received in route
    try:
        _log_path = Path(__file__).parent.parent.parent.parent.parent / ".cursor" / "debug.log"
        with open(_log_path, "a", encoding="utf-8") as _f:
            _f.write(json.dumps({"message": "forecast_route_body", "order_id": order_id, "body_len": len(body_bytes) if body_bytes else 0, "body_preview": (body_bytes.decode("utf-8", errors="replace")[:200] if body_bytes else ""), "timestamp": __import__("time").time()}) + "\n")
    except Exception:
        pass
    # #endregion
    if not body_bytes:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=[{"type": "missing", "loc": ["body"], "msg": "Field required"}])
    try:
        request_model = ForecastRequest.model_validate_json(body_bytes.decode("utf-8"))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=[{"type": "value_error", "loc": ["body"], "msg": str(e)}])
    result = calculate_eta(
        order_id=order_id,
        destination_latitude=request_model.destination_latitude,
        destination_longitude=request_model.destination_longitude,
        priority=request_model.priority,
    )
    
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No telemetry data found for order ID: {order_id}"
        )
    
    return ForecastResponse(
        distance_km=result["distance_km"],
        estimated_arrival_minutes=result["estimated_arrival_minutes"]
    )
