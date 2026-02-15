import type { Order } from './types'

const ORDERS_URL = 'http://localhost:8082/api/orders'

export async function fetchOrders(): Promise<Order[]> {
  const res = await fetch(ORDERS_URL)
  if (!res.ok) {
    throw new Error(`Orders API error: ${res.status} ${res.statusText}`)
  }
  return res.json() as Promise<Order[]>
}
