import { useState } from 'react'
import { postAssistantChat } from '../api/assistantClient'

export type ChatMessage = { role: 'user' | 'assistant'; text: string }

interface AssistantChatProps {
  selectedOrderId: string | null
}

export function AssistantChat({ selectedOrderId }: AssistantChatProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const trimmed = input.trim()
    if (!trimmed || !selectedOrderId) return
    setMessages((prev) => [...prev, { role: 'user', text: trimmed }])
    setInput('')
    setLoading(true)
    try {
      const reply = await postAssistantChat(selectedOrderId, trimmed)
      setMessages((prev) => [...prev, { role: 'assistant', text: reply }])
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          text: err instanceof Error ? err.message : 'Failed to get a response.',
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      {/* Floating bubble */}
      <button
        type="button"
        onClick={() => setIsOpen((o) => !o)}
        className="fixed bottom-6 right-6 z-50 flex h-14 w-14 items-center justify-center rounded-full bg-emerald-600 text-white shadow-lg transition hover:bg-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:ring-offset-2 focus:ring-offset-slate-900"
        aria-label={isOpen ? 'Close assistant' : 'Open Logistics Assistant'}
      >
        <span className="text-xl" aria-hidden>{isOpen ? '✕' : '◆'}</span>
      </button>

      {/* Expanded chat window */}
      {isOpen && (
        <div className="fixed bottom-24 right-6 z-40 flex h-[420px] w-[380px] flex-col rounded-xl border border-slate-700 bg-slate-900 shadow-xl">
          <div className="border-b border-slate-700 px-4 py-3">
            <h2 className="text-sm font-semibold text-slate-100">Logistics Assistant</h2>
            <p className="text-xs text-slate-400">Context-aware support</p>
          </div>
          <div className="flex-1 overflow-y-auto p-3">
            {messages.length === 0 && !loading ? (
              <p className="text-sm text-slate-500">No messages yet. Say hello.</p>
            ) : (
              <ul className="space-y-3">
                {messages.map((m, i) => (
                  <li
                    key={i}
                    className={`text-sm ${m.role === 'user' ? 'text-right' : 'text-left'}`}
                  >
                    <span
                      className={`inline-block max-w-[85%] rounded-lg px-3 py-2 ${
                        m.role === 'user'
                          ? 'bg-emerald-600/80 text-white'
                          : 'bg-slate-700 text-slate-200'
                      }`}
                    >
                      {m.text}
                    </span>
                  </li>
                ))}
                {loading && (
                  <li className="text-left text-sm">
                    <span className="inline-block rounded-lg bg-slate-700 px-3 py-2 text-slate-300">
                      Claude is thinking…
                    </span>
                  </li>
                )}
              </ul>
            )}
          </div>
          <form onSubmit={handleSubmit} className="flex gap-2 border-t border-slate-700 p-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type a message…"
              disabled={!selectedOrderId || loading}
              className="flex-1 rounded-lg border border-slate-600 bg-slate-800 px-3 py-2 text-sm text-slate-100 placeholder-slate-500 focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
            />
            <button
              type="submit"
              disabled={!selectedOrderId || loading}
              className="rounded-lg bg-emerald-600 px-3 py-2 text-sm font-medium text-white hover:bg-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:ring-offset-2 focus:ring-offset-slate-900 disabled:opacity-50"
            >
              Send
            </button>
          </form>
        </div>
      )}
    </>
  )
}
