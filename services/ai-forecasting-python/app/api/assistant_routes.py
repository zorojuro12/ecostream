"""
Logistics Assistant API.
Exposes POST /api/assistant/chat for grounded Q&A with distance/ETA context.
"""
from fastapi import APIRouter

from app.api.schemas import AssistantChatRequest, AssistantChatResponse
from app.engine.bedrock_client import get_bedrock_client
from app.services.assistant_service import chat

router = APIRouter(prefix="/api/assistant", tags=["assistant"])


@router.post("/chat", response_model=AssistantChatResponse)
def assistant_chat(body: AssistantChatRequest) -> AssistantChatResponse:
    """
    Send a message to the EcoStream Logistics Assistant.
    The assistant is grounded with live distance and ETA for the order.
    """
    client = get_bedrock_client()
    reply = chat(
        client=client,
        order_id=body.order_id,
        user_message=body.message,
        destination_latitude=body.destination_latitude,
        destination_longitude=body.destination_longitude,
        priority=body.priority,
    )
    return AssistantChatResponse(reply=reply)
