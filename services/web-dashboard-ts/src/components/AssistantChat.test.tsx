import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { AssistantChat } from './AssistantChat'

vi.mock('../api/assistantClient', () => ({
  postAssistantChat: vi.fn(),
}))

import { postAssistantChat } from '../api/assistantClient'
const mockPost = vi.mocked(postAssistantChat)

describe('AssistantChat', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the floating bubble button', () => {
    render(<AssistantChat selectedOrderId={null} />)
    expect(
      screen.getByRole('button', { name: 'Open Logistics Assistant' }),
    ).toBeInTheDocument()
  })

  it('opens the chat window when bubble is clicked', async () => {
    render(<AssistantChat selectedOrderId="order-1" />)
    await userEvent.click(
      screen.getByRole('button', { name: 'Open Logistics Assistant' }),
    )
    expect(screen.getByText('Logistics Assistant')).toBeInTheDocument()
    expect(screen.getByText('No messages yet. Say hello.')).toBeInTheDocument()
  })

  it('shows prompt to select an order when none is selected', async () => {
    render(<AssistantChat selectedOrderId={null} />)
    await userEvent.click(
      screen.getByRole('button', { name: 'Open Logistics Assistant' }),
    )
    expect(
      screen.getByText('Please select an order to chat with the Logistics Assistant.'),
    ).toBeInTheDocument()
  })

  it('sends a message and displays the assistant reply', async () => {
    mockPost.mockResolvedValueOnce('ETA is approximately 25 minutes.')

    render(<AssistantChat selectedOrderId="order-1" />)
    await userEvent.click(
      screen.getByRole('button', { name: 'Open Logistics Assistant' }),
    )

    const input = screen.getByPlaceholderText('Type a message…')
    await userEvent.type(input, 'What is my ETA?')
    await userEvent.click(screen.getByRole('button', { name: 'Send' }))

    expect(screen.getByText('What is my ETA?')).toBeInTheDocument()
    await waitFor(() => {
      expect(screen.getByText('ETA is approximately 25 minutes.')).toBeInTheDocument()
    })
    expect(mockPost).toHaveBeenCalledWith('order-1', 'What is my ETA?')
  })

  it('displays error message when assistant call fails', async () => {
    mockPost.mockRejectedValueOnce(new Error('Network error'))

    render(<AssistantChat selectedOrderId="order-1" />)
    await userEvent.click(
      screen.getByRole('button', { name: 'Open Logistics Assistant' }),
    )

    const input = screen.getByPlaceholderText('Type a message…')
    await userEvent.type(input, 'Hello')
    await userEvent.click(screen.getByRole('button', { name: 'Send' }))

    await waitFor(() => {
      expect(screen.getByText('Network error')).toBeInTheDocument()
    })
  })
})
