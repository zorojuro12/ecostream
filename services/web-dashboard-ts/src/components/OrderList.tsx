import type { Order } from '../api/types'

interface OrderListProps {
  orders: Order[]
}

export function OrderList({ orders }: OrderListProps) {
  return (
    <ul>
      {orders.map((order) => (
        <li key={order.id}>
          <span data-testid="order-id">{order.id}</span>
          {' | '}
          <span data-testid="order-status">{order.status}</span>
          {order.estimatedArrivalMinutes != null && (
            <>
              {' | ETA: '}
              <span data-testid="order-eta">{order.estimatedArrivalMinutes}</span>
              {' min'}
            </>
          )}
        </li>
      ))}
    </ul>
  )
}
