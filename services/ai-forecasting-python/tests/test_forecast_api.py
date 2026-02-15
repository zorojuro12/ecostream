"""
TDD: Forecast API must accept the exact JSON body the Java client sends (snake_case).
Definition of Done: POST /api/forecast/{order_id} with that body must NOT return 422.
"""
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


# Exact payload shape Java sends (ForecastRequestDTO with @JsonProperty snake_case)
JAVA_CLIENT_BODY = {
    "destination_latitude": 49.2276,
    "destination_longitude": -123.0076,
    "priority": "Standard",
}


def test_forecast_post_accepts_java_payload_no_422():
    """
    When the Java client POSTs to /api/forecast/{order_id} with destination_latitude,
    destination_longitude, and priority (snake_case), the API must not return 422.
    Either 200 (with distance_km, estimated_arrival_minutes) or 404 (no telemetry) is acceptable.
    """
    client = TestClient(app)
    order_id = "e4b6afa3-ea79-45dd-a69b-4e60352067d2"

    with patch("app.api.forecasting_routes.calculate_eta") as mock_eta:
        mock_eta.return_value = {
            "distance_km": 12.5,
            "estimated_arrival_minutes": 25.0,
        }

        response = client.post(
            f"/api/forecast/{order_id}",
            json=JAVA_CLIENT_BODY,
            headers={"Content-Type": "application/json"},
        )

    assert response.status_code != 422, (
        f"Forecast API must accept Java client body. Got 422: {response.json()}"
    )
    if response.status_code == 200:
        data = response.json()
        assert "distance_km" in data
        assert "estimated_arrival_minutes" in data


def test_forecast_post_with_raw_bytes_snake_case():
    """
    Send body as raw bytes (simulating wire format) with snake_case keys.
    Ensures the app accepts the body when received as in production.
    """
    import json
    client = TestClient(app)
    order_id = "56957687-34d2-40dc-8da4-f10cebacbcc5"
    body_bytes = json.dumps(JAVA_CLIENT_BODY).encode("utf-8")

    with patch("app.api.forecasting_routes.calculate_eta") as mock_eta:
        mock_eta.return_value = {
            "distance_km": 10.0,
            "estimated_arrival_minutes": 20.0,
        }

        response = client.post(
            f"/api/forecast/{order_id}",
            content=body_bytes,
            headers={"Content-Type": "application/json"},
        )

    assert response.status_code != 422, (
        f"Forecast API must accept raw JSON body. Got 422: {response.json()}"
    )
