"""
TDD: POST /api/assistant/chat must return real Bedrock reply when client succeeds.
When Bedrock is available (or mocked), response must NOT be the fallback message.
"""
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app

# Fallback returned when Bedrock fails or credentials missing (same as bedrock_client)
FALLBACK = "My satellite link is currently updating. Please check back in 2 minutes!"


def test_assistant_chat_returns_real_reply_when_bedrock_succeeds():
    """
    When get_bedrock_client returns a client that succeeds at converse(),
    the API response must contain that reply, not the fallback.
    (Reproduces: aws-test.py works, curl returns fallback -> ensure app uses same env/client behavior.)
    """
    mock_client = MagicMock()
    mock_client.converse.return_value = {
        "output": {
            "message": {
                "content": [{"text": "Congestion on the route is likely the cause."}],
            },
        },
    }

    with patch("app.api.assistant_routes.get_bedrock_client", return_value=mock_client), patch(
        "app.services.assistant_service._fetch_order_from_order_service",
        return_value={"destination": {"latitude": 49.28, "longitude": -123.12}, "priority": 3},
    ), patch(
        "app.services.assistant_service.calculate_eta",
        return_value={"distance_km": 3.1, "estimated_arrival_minutes": 5.0},
    ):
        client = TestClient(app)
        response = client.post(
            "/api/assistant/chat",
            json={
                "order_id": "e4b6afa3-ea79-45dd-a69b-4e60352067d2",
                "message": "Based on my current speed, why am I delayed?",
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert data["reply"] != FALLBACK, (
        "Assistant must return real Bedrock reply when client succeeds, not fallback. "
        "Check that the app loads .env before creating the Bedrock client (same as aws-test.py)."
    )
    assert "Congestion" in data["reply"]
