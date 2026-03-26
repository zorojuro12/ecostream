"""
Forecasting Service — orchestrates telemetry retrieval and ETA calculation.

Uses the trained ML model (or heuristic fallback) to predict delivery speed
based on distance, time-of-day, day-of-week, month, and order priority.
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from app.engine.forecaster import calculate_haversine_distance
from app.engine.model_loader import predict_speed
from app.services.telemetry_service import get_latest_telemetry

logger = logging.getLogger(__name__)


def calculate_eta(
    order_id: str,
    destination_latitude: float,
    destination_longitude: float,
    priority: str = "Standard",
) -> Optional[dict]:
    """Calculate Estimated Time of Arrival for an order.

    Fetches the latest telemetry position, computes Haversine distance to
    destination, then predicts delivery speed using the ML model with
    time-of-day context.

    Returns:
        Dict with 'distance_km' and 'estimated_arrival_minutes', or None
        if no telemetry exists for the order.
    """
    current_location = get_latest_telemetry(order_id)

    if current_location is None:
        logger.warning("No telemetry data found for orderId: %s", order_id)
        return None

    distance_km = calculate_haversine_distance(
        lat1=current_location.latitude,
        lon1=current_location.longitude,
        lat2=destination_latitude,
        lon2=destination_longitude,
    )

    now = datetime.now(timezone.utc)
    speed_kmh = predict_speed(
        distance_km=distance_km,
        hour_of_day=now.hour,
        day_of_week=now.weekday(),
        month=now.month,
        priority=priority,
    )

    if speed_kmh <= 0:
        logger.error("Model returned non-positive speed (%.2f) for orderId %s", speed_kmh, order_id)
        speed_kmh = 10.0

    estimated_arrival_minutes = (distance_km / speed_kmh) * 60

    logger.info(
        "ETA calculated for orderId %s: %.2f km, %.1f min (priority=%s, speed=%.1f km/h, hour=%d)",
        order_id,
        distance_km,
        estimated_arrival_minutes,
        priority,
        speed_kmh,
        now.hour,
    )

    return {
        "distance_km": round(distance_km, 2),
        "estimated_arrival_minutes": round(estimated_arrival_minutes, 1),
    }
