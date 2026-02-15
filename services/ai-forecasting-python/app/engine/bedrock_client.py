"""
Bedrock Converse API client for the EcoStream Logistics Assistant.
Uses boto3 bedrock-runtime and anthropic.claude-3-5-haiku in us-east-1.
"""
import logging
from typing import Optional

import boto3

logger = logging.getLogger(__name__)

MODEL_ID = "anthropic.claude-3-5-haiku-20241022-v1:0"
ACCESS_DENIED_FALLBACK = (
    "My satellite link is currently updating. Please check back in 2 minutes!"
)


def get_bedrock_client():
    """Return a Bedrock Runtime client for us-east-1 (verified region)."""
    return boto3.client("bedrock-runtime", region_name="us-east-1")


def get_ai_insight(
    client,
    user_message: str,
    system_prompt: Optional[str] = None,
) -> str:
    """
    Call Bedrock Converse API and return the assistant's text response.
    On AccessDeniedException, returns a friendly fallback message.
    """
    try:
        kwargs = {
            "modelId": MODEL_ID,
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": user_message}],
                },
            ],
        }
        if system_prompt:
            kwargs["system"] = [{"text": system_prompt}]

        response = client.converse(**kwargs)
        content_blocks = response.get("output", {}).get("message", {}).get("content", [])
        if not content_blocks:
            return ACCESS_DENIED_FALLBACK
        text_block = content_blocks[0]
        return text_block.get("text", "") or ACCESS_DENIED_FALLBACK
    except client.exceptions.AccessDeniedException:
        logger.warning("Bedrock AccessDeniedException; returning fallback message")
        return ACCESS_DENIED_FALLBACK
    except Exception as e:
        logger.exception("Bedrock converse failed: %s", e)
        return ACCESS_DENIED_FALLBACK
