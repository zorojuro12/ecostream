"""
Pydantic schemas for request/response validation.
Mirrors Java service validation rules for coordinate parity.
"""
from pydantic import BaseModel, ConfigDict, Field


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


class ForecastRequest(BaseModel):
    """
    Request body for forecasting endpoint.
    Accepts snake_case or camelCase for Java client compatibility.
    """
    model_config = ConfigDict(populate_by_name=True)

    destination_latitude: float = Field(
        ...,
        ge=-90.0,
        le=90.0,
        alias="destinationLatitude",
        description="Destination latitude. Must be between -90 and 90 degrees (inclusive)."
    )
    destination_longitude: float = Field(
        ...,
        ge=-180.0,
        le=180.0,
        alias="destinationLongitude",
        description="Destination longitude. Must be between -180 and 180 degrees (inclusive)."
    )
    priority: str = Field(
        default="Standard",
        description="Order priority for speed prediction: Express (faster) or Standard (slower)."
    )


class ForecastResponse(BaseModel):
    """
    Response from forecasting endpoint.
    Contains distance and estimated arrival time.
    """
    distance_km: float = Field(..., description="Distance to destination in kilometers")
    estimated_arrival_minutes: float = Field(..., description="Estimated arrival time in minutes")


class AssistantChatRequest(BaseModel):
    """Request body for Logistics Assistant chat (POST /api/assistant/chat). Destination/priority from Order Service (SSoT)."""
    order_id: str = Field(..., description="Order ID; destination and priority are fetched from Order Service")
    message: str = Field(..., min_length=1, description="User question for the assistant")


class AssistantChatResponse(BaseModel):
    """Response from Logistics Assistant chat."""
    reply: str = Field(..., description="Assistant reply (grounded with distance/ETA)")
