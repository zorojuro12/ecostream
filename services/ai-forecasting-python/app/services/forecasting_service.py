"""
Forecasting Service
Orchestrates telemetry retrieval and ETA calculation using ML-predicted speed.
"""
import logging
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
    """
    Calculate Estimated Time of Arrival (ETA) for an order.

    Uses ML-predicted speed from priority (Express = faster, Standard = slower).

    Args:
        order_id: The order ID to calculate ETA for
        destination_latitude: Destination latitude coordinate
        destination_longitude: Destination longitude coordinate
        priority: Order priority for speed prediction (Express or Standard)

    Returns:
        Dictionary with 'distance_km' and 'estimated_arrival_minutes', or None if telemetry not found
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

    speed_kmh = predict_speed(priority)
    estimated_arrival_hours = distance_km / speed_kmh
    estimated_arrival_minutes = estimated_arrival_hours * 60

    logger.info(
        "ETA calculated for orderId %s: %s km, %s minutes (priority=%s, speed=%s km/h)",
        order_id,
        f"{distance_km:.2f}",
        f"{estimated_arrival_minutes:.1f}",
        priority,
        speed_kmh,
    )

    return {
        "distance_km": round(distance_km, 2),
        "estimated_arrival_minutes": round(estimated_arrival_minutes, 1),
    }
