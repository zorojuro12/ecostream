"""
Logistics Assistant service: grounds user questions with live distance/ETA data
and calls the Bedrock AI (EcoStream Logistics Assistant).
"""
import logging
from typing import Any, Optional

from app.engine.bedrock_client import get_ai_insight
from app.services.forecasting_service import calculate_eta

logger = logging.getLogger(__name__)

SYSTEM_IDENTITY = "You are the EcoStream Logistics Assistant."


def chat(
    client: Any,
    order_id: str,
    user_message: str,
    destination_latitude: float,
    destination_longitude: float,
    priority: str = "Standard",
) -> str:
    """
    Answer the user's question using live distance and ETA, then the Bedrock model.
    Injects context in XML format: <context>Distance: Xkm, ETA: Ymin</context>.
    """
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
