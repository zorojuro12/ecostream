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
    Destination and priority are fetched from the Order Service (SSoT); distance/ETA are grounded.
    """
    client = get_bedrock_client()
    reply = chat(
        client=client,
        order_id=body.order_id,
        user_message=body.message,
    )
    return AssistantChatResponse(reply=reply)
