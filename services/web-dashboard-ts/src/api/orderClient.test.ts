import { describe, it, expect, vi, beforeEach } from 'vitest'
import { fetchOrders } from './orderClient'

describe('orderClient', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('fetchOrders() returns a list of orders including distanceKm and estimatedArrivalMinutes', async () => {
    const mockOrders = [
      {
        id: '550e8400-e29b-41d4-a716-446655440000',
        status: 'PENDING',
        destination: { latitude: 49.28, longitude: -123.11 },
        priority: 5,
        distanceKm: 13.72,
        estimatedArrivalMinutes: 25.5,
      },
    ]
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockOrders),
    } as Response)

    const result = await fetchOrders()

    expect(result).toHaveLength(1)
    expect(result[0]).toHaveProperty('distanceKm', 13.72)
    expect(result[0]).toHaveProperty('estimatedArrivalMinutes', 25.5)
    expect(result[0].id).toBe(mockOrders[0].id)
    expect(result[0].status).toBe(mockOrders[0].status)
  })
})
