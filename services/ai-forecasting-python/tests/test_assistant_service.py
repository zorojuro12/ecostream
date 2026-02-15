"""
TDD: Logistics Assistant service with data grounding.
Uses Order Service as SSoT for destination/priority; injects distance/ETA into prompt.
"""
from unittest.mock import MagicMock, patch

from app.services import assistant_service


def test_assistant_chat_fetches_order_then_injects_distance_and_eta_into_prompt():
    """
    chat() must fetch order from Order Service, call forecaster for ETA with that
    destination/priority, build context in XML, and call get_ai_insight; return the AI string.
    """
    mock_order = {
        "id": "test-order-123",
        "destination": {"latitude": 49.28, "longitude": -123.12},
        "priority": 5,
    }
    mock_eta = {"distance_km": 5.2, "estimated_arrival_minutes": 12.0}
    mock_ai_response = "Based on your current speed, congestion on the route is likely the cause."

    with patch(
        "app.services.assistant_service._fetch_order_from_order_service",
        return_value=mock_order,
    ), patch(
        "app.services.assistant_service.calculate_eta", return_value=mock_eta
    ) as mock_eta_fn, patch(
        "app.services.assistant_service.get_ai_insight", return_value=mock_ai_response
    ) as mock_insight:
        mock_client = MagicMock()
        result = assistant_service.chat(
            client=mock_client,
            order_id="test-order-123",
            user_message="Based on my current speed, why am I delayed?",
        )

    mock_eta_fn.assert_called_once_with(
        order_id="test-order-123",
        destination_latitude=49.28,
        destination_longitude=-123.12,
        priority="Express",
    )
    mock_insight.assert_called_once()
    call_args = mock_insight.call_args
    kwargs = call_args[1] if call_args[1] else {}
    assert kwargs.get("user_message") == "Based on my current speed, why am I delayed?"
    system_prompt = kwargs.get("system_prompt", "")
    assert "EcoStream Logistics Assistant" in system_prompt
    assert "<context>" in system_prompt and "</context>" in system_prompt
    assert "5.2" in system_prompt and "12.0" in system_prompt
    assert "km" in system_prompt.lower() and "min" in system_prompt.lower()
    assert result == mock_ai_response
