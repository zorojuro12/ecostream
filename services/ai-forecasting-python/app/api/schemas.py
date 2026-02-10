"""
Pydantic schemas for request/response validation.
Mirrors Java service validation rules for coordinate parity.
"""
from pydantic import BaseModel, Field


class Location(BaseModel):
    """
    Geographic location coordinates.
    Used for order destinations and telemetry tracking.
    
    Validation matches Java LocationDTO:
    - Latitude: -90.0 to 90.0 (inclusive)
    - Longitude: -180.0 to 180.0 (inclusive)
    """
    latitude: float = Field(
        ...,
        ge=-90.0,
        le=90.0,
        description="Latitude coordinate. Must be between -90 and 90 degrees (inclusive)."
    )
    longitude: float = Field(
        ...,
        ge=-180.0,
        le=180.0,
        description="Longitude coordinate. Must be between -180 and 180 degrees (inclusive)."
    )
