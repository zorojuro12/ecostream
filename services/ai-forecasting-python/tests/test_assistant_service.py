"""
TDD: Logistics Assistant service with data grounding.
Step 3: Assistant injects distance and ETA into prompt context before calling AI.
"""
import pytest
from unittest.mock import MagicMock, patch

from app.services import assistant_service


def test_assistant_chat_injects_distance_and_eta_into_prompt_and_returns_ai_response():
    """
    chat() must call the forecaster for ETA, build context with distance and ETA
    in XML format, and call get_ai_insight with that context; return the AI string.
    """
    mock_eta = {"distance_km": 5.2, "estimated_arrival_minutes": 12.0}
    mock_ai_response = "Based on your current speed, congestion on the route is likely the cause."

    with patch(
        "app.services.assistant_service.calculate_eta", return_value=mock_eta
    ) as mock_eta_fn, patch(
        "app.services.assistant_service.get_ai_insight", return_value=mock_ai_response
    ) as mock_insight:
        mock_client = MagicMock()
        result = assistant_service.chat(
            client=mock_client,
            order_id="test-order-123",
            user_message="Based on my current speed, why am I delayed?",
            destination_latitude=49.28,
            destination_longitude=-123.12,
            priority="Standard",
        )

    mock_eta_fn.assert_called_once_with(
        order_id="test-order-123",
        destination_latitude=49.28,
        destination_longitude=-123.12,
        priority="Standard",
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
