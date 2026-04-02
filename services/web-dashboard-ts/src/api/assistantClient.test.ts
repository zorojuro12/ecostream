import { describe, it, expect, vi, beforeEach } from 'vitest'
import { postAssistantChat } from './assistantClient'

describe('assistantClient', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('posts order_id and message then returns the reply string', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ reply: 'The shipment is on track.' }),
    } as Response)

    const result = await postAssistantChat('abc-123', 'Where is my order?')

    expect(result).toBe('The shipment is on track.')
    expect(globalThis.fetch).toHaveBeenCalledWith(
      'http://localhost:5050/api/assistant/chat',
      expect.objectContaining({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ order_id: 'abc-123', message: 'Where is my order?' }),
      }),
    )
  })

  it('throws on non-ok response', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error',
    } as Response)

    await expect(postAssistantChat('abc', 'hi')).rejects.toThrow(
      'Assistant API error: 500 Internal Server Error',
    )
  })
})
