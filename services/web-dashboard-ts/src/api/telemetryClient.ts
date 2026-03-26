/** Fetches latest telemetry position for an order from the AI service. */
export interface TelemetryPosition {
  latitude: number
  longitude: number
}

const TELEMETRY_BASE = 'http://localhost:5050/api/test/telemetry'

export async function fetchTelemetry(orderId: string): Promise<TelemetryPosition | null> {
  const res = await fetch(`${TELEMETRY_BASE}/${orderId}`)
  if (!res.ok) return null
  const data = await res.json()
  if (!data || data.latitude == null || data.longitude == null) return null
  return { latitude: data.latitude, longitude: data.longitude }
}
