"""
Logistics Assistant service: grounds user questions with live distance/ETA data
and calls the Bedrock AI (EcoStream Logistics Assistant).
Uses Order Service as Single Source of Truth for order destination and priority.
"""
import logging
import os
from typing import Any, Optional

import httpx

from app.engine.bedrock_client import get_ai_insight
from app.services.forecasting_service import calculate_eta

logger = logging.getLogger(__name__)

SYSTEM_IDENTITY = "You are the EcoStream Logistics Assistant."

ORDER_SERVICE_BASE_URL = os.getenv("ORDER_SERVICE_BASE_URL", "http://localhost:8082")


def _fetch_order_from_order_service(order_id: str) -> Optional[dict]:
    """
    Fetch order details (destination lat/lon, priority) from Java Order Service.
    Single Source of Truth for order destination. Returns None on 404 or error.
    """
    url = f"{ORDER_SERVICE_BASE_URL.rstrip('/')}/api/orders/{order_id}"
    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(url)
            if resp.status_code == 404:
                logger.warning("Order not found: %s", order_id)
                return None
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPError as e:
        logger.warning("Failed to fetch order %s from Order Service: %s", order_id, e)
        return None


def _order_to_destination_and_priority(order: dict) -> Optional[tuple[float, float, str]]:
    """Extract destination latitude, longitude, and priority string from order JSON."""
    dest = order.get("destination") or {}
    lat = dest.get("latitude")
    lon = dest.get("longitude")
    if lat is None or lon is None:
        return None
    priority_int = order.get("priority")
    priority_str = "Express" if (priority_int is not None and priority_int >= 5) else "Standard"
    return (float(lat), float(lon), priority_str)


def chat(client: Any, order_id: str, user_message: str) -> str:
    """
    Answer the user's question using live distance and ETA, then the Bedrock model.
    Fetches order destination and priority from Order Service (SSoT), then uses
    Haversine + telemetry for distance/ETA. Injects context in XML format.
    """
    order = _fetch_order_from_order_service(order_id)
    if order is None:
        return (
            "I couldn't find that order. Please check the order ID or try again later."
        )
    dest_priority = _order_to_destination_and_priority(order)
    if dest_priority is None:
        return (
            "That order has no destination set. I need a destination to compute distance and ETA."
        )
    destination_latitude, destination_longitude, priority = dest_priority

    # Pass Order Service (SSoT) coordinates into Haversine/ETA so dashboard and assistant match.
    eta_result = calculate_eta(
        order_id=order_id,
        destination_latitude=destination_latitude,
        destination_longitude=destination_longitude,
        priority=priority,
    )

    if eta_result is None:
        return (
            "I don't have live position data for this order yet. "
            "Please ensure telemetry is being sent, then try again."
        )

    distance_km = eta_result["distance_km"]
    eta_min = eta_result["estimated_arrival_minutes"]
    context = f"<context>Distance: {distance_km}km, ETA: {eta_min}min</context>"
    system_prompt = f"{SYSTEM_IDENTITY}\n{context}"

    return get_ai_insight(
        client=client,
        user_message=user_message,
        system_prompt=system_prompt,
    )
