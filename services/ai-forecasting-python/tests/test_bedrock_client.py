"""
TDD: Bedrock Converse client for Logistics Assistant.
Step 1 (Red): Test that get_ai_insight uses converse() and returns a string.
"""
import pytest
from unittest.mock import MagicMock, patch

# Import after patching so we use the mock client
from app.engine import bedrock_client


def test_get_ai_insight_calls_converse_and_returns_string():
    """
    get_ai_insight must call the bedrock-runtime client's converse() once
    and return the assistant's text response as a string.
    """
    mock_client = MagicMock()
    mock_client.converse.return_value = {
        "output": {
            "message": {
                "content": [{"text": "Based on your current speed, traffic is likely the cause."}],
            },
        },
    }

    result = bedrock_client.get_ai_insight(mock_client, "Why am I delayed?")

    mock_client.converse.assert_called_once()
    call_kw = mock_client.converse.call_args.kwargs
    assert "modelId" in call_kw
    assert "messages" in call_kw
    assert call_kw["messages"][0]["role"] == "user"
    assert call_kw["messages"][0]["content"][0]["text"] == "Why am I delayed?"
    assert result == "Based on your current speed, traffic is likely the cause."
    assert isinstance(result, str)


def test_get_ai_insight_returns_fallback_on_access_denied():
    """On AccessDeniedException, return friendly fallback message."""
    mock_client = MagicMock()
    mock_client.converse.side_effect = mock_client.exceptions.AccessDeniedException(
        {"Error": {"Code": "AccessDeniedException", "Message": "Access Denied"}}, "Converse"
    )
    # Ensure exceptions.AccessDeniedException exists on the mock
    if not hasattr(mock_client, "exceptions"):
        mock_client.exceptions = MagicMock()
    mock_client.exceptions.AccessDeniedException = type(
        "AccessDeniedException", (Exception,), {}
    )
    mock_client.converse.side_effect = mock_client.exceptions.AccessDeniedException()

    result = bedrock_client.get_ai_insight(mock_client, "Hello")

    assert bedrock_client.ACCESS_DENIED_FALLBACK in result or "satellite" in result.lower()
