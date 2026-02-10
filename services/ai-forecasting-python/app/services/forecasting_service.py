"""
Forecasting Service
Orchestrates telemetry retrieval and ETA calculation.
"""
import logging
from typing import Optional

from app.api.schemas import Location
from app.services.telemetry_service import get_latest_telemetry
from app.engine.forecaster import calculate_haversine_distance

logger = logging.getLogger(__name__)

# Default constant speed for ETA calculation (km/h)
# This is a placeholder until ML model is integrated
DEFAULT_SPEED_KMH = 40.0


def calculate_eta(
    order_id: str,
    destination_latitude: float,
    destination_longitude: float
) -> Optional[dict]:
    """
    Calculate Estimated Time of Arrival (ETA) for an order.
    
    Retrieves the latest telemetry data for the order, calculates the distance
    to the destination, and estimates arrival time based on a constant speed.
    
    Args:
        order_id: The order ID to calculate ETA for
        destination_latitude: Destination latitude coordinate
        destination_longitude: Destination longitude coordinate
        
    Returns:
        Dictionary with 'distance_km' and 'estimated_arrival_minutes', or None if telemetry not found
    """
    # Retrieve latest telemetry data
    current_location = get_latest_telemetry(order_id)
    
    if current_location is None:
        logger.warning(f"No telemetry data found for orderId: {order_id}")
        return None
    
    # Calculate distance using Haversine formula
    distance_km = calculate_haversine_distance(
        lat1=current_location.latitude,
        lon1=current_location.longitude,
        lat2=destination_latitude,
        lon2=destination_longitude
    )
    
    # Calculate ETA based on constant speed (placeholder for ML model)
    # Time = Distance / Speed
    estimated_arrival_hours = distance_km / DEFAULT_SPEED_KMH
    estimated_arrival_minutes = estimated_arrival_hours * 60
    
    logger.info(
        f"ETA calculated for orderId {order_id}: "
        f"{distance_km:.2f} km, {estimated_arrival_minutes:.1f} minutes"
    )
    
    return {
        "distance_km": round(distance_km, 2),
        "estimated_arrival_minutes": round(estimated_arrival_minutes, 1)
    }
