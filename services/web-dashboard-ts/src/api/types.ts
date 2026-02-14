/** Matches OrderResponseDTO from Java Order Service (port 8082). */
export interface Order {
  id: string
  status: 'PENDING' | 'CONFIRMED' | 'IN_TRANSIT' | 'DELIVERED' | 'CANCELLED'
  destination: { latitude: number; longitude: number }
  priority: number | null
  distanceKm: number | null
  estimatedArrivalMinutes: number | null
}
