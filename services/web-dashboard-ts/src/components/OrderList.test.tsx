import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { OrderList } from './OrderList'
import type { Order } from '../api/types'

const sampleOrders: Order[] = [
  {
    id: '550e8400-e29b-41d4-a716-446655440000',
    status: 'IN_TRANSIT',
    destination: { latitude: 49.28, longitude: -123.11 },
    priority: 5,
    distanceKm: 13.72,
    estimatedArrivalMinutes: 25.5,
  },
  {
    id: 'aaaa1111-bbbb-2222-cccc-333344445555',
    status: 'PENDING',
    destination: { latitude: 49.2, longitude: -123.0 },
    priority: 1,
    distanceKm: null,
    estimatedArrivalMinutes: null,
  },
]

describe('OrderList', () => {
  it('renders empty state when no orders', () => {
    render(
      <OrderList orders={[]} selectedOrderId={null} onSelectOrder={() => {}} />,
    )
    expect(screen.getByText('No orders yet.')).toBeInTheDocument()
  })

  it('renders order rows with id, status, distance, and ETA', () => {
    render(
      <OrderList
        orders={sampleOrders}
        selectedOrderId={null}
        onSelectOrder={() => {}}
      />,
    )
    const ids = screen.getAllByTestId('order-id')
    expect(ids).toHaveLength(2)
    expect(ids[0]).toHaveTextContent('550e8400-e29b-41d4-a716-446655440000')

    const statuses = screen.getAllByTestId('order-status')
    expect(statuses[0]).toHaveTextContent('IN_TRANSIT')
    expect(statuses[1]).toHaveTextContent('PENDING')

    const etas = screen.getAllByTestId('order-eta')
    expect(etas[0]).toHaveTextContent('25.5 min')
    expect(etas[1]).toHaveTextContent('—')
  })

  it('calls onSelectOrder when a row is clicked', async () => {
    const onSelect = vi.fn()
    render(
      <OrderList
        orders={sampleOrders}
        selectedOrderId={null}
        onSelectOrder={onSelect}
      />,
    )
    const rows = screen.getAllByRole('button')
    await userEvent.click(rows[0])
    expect(onSelect).toHaveBeenCalledWith('550e8400-e29b-41d4-a716-446655440000')
  })

  it('highlights the selected order row', () => {
    const { container } = render(
      <OrderList
        orders={sampleOrders}
        selectedOrderId="550e8400-e29b-41d4-a716-446655440000"
        onSelectOrder={() => {}}
      />,
    )
    const rows = container.querySelectorAll('tr[role="button"]')
    expect(rows[0].className).toContain('bg-emerald-900/30')
    expect(rows[1].className).not.toContain('bg-emerald-900/30')
  })

  it('shows live-tracking pulse when liveTracking is true', () => {
    render(
      <OrderList
        orders={sampleOrders}
        liveTracking={true}
        selectedOrderId={null}
        onSelectOrder={() => {}}
      />,
    )
    expect(screen.getByTitle('Live tracking')).toBeInTheDocument()
  })
})
