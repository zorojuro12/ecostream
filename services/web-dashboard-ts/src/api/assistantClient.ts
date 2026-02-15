const ASSISTANT_URL = 'http://localhost:5050/api/assistant/chat'

export interface AssistantChatResponse {
  reply: string
}

export async function postAssistantChat(
  orderId: string,
  message: string
): Promise<string> {
  const res = await fetch(ASSISTANT_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ order_id: orderId, message }),
  })
  if (!res.ok) {
    throw new Error(`Assistant API error: ${res.status} ${res.statusText}`)
  }
  const data = (await res.json()) as AssistantChatResponse
  return data.reply
}
