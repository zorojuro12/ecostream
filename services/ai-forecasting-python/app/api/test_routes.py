"""
Test routes for verifying DynamoDB connectivity and telemetry retrieval.
"""
from fastapi import APIRouter
from typing import Optional

from app.api.schemas import Location
from app.services.telemetry_service import get_latest_telemetry

router = APIRouter(prefix="/api/test", tags=["test"])


@router.get("/telemetry/{order_id}", response_model=Optional[Location])
async def test_telemetry_retrieval(order_id: str):
    """
    Test endpoint to retrieve the latest telemetry data for a given order ID.
    
    Args:
        order_id: The order ID to query
        
    Returns:
        Location object with the latest coordinates, or null if not found
    """
    location = get_latest_telemetry(order_id)
    
    if location is None:
        return None
    
    return location
