import { useEffect, useRef, useMemo } from 'react'
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet'
import L from 'leaflet'

import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png'
import markerIcon from 'leaflet/dist/images/marker-icon.png'
import markerShadow from 'leaflet/dist/images/marker-shadow.png'

// Fix Leaflet default marker icons broken by bundlers
delete (L.Icon.Default.prototype as unknown as Record<string, unknown>)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
})

const destinationIcon = new L.Icon({
  iconUrl: markerIcon,
  iconRetinaUrl: markerIcon2x,
  shadowUrl: markerShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
})

const vehicleIcon = new L.Icon({
  iconUrl: markerIcon,
  iconRetinaUrl: markerIcon2x,
  shadowUrl: markerShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
  className: 'leaflet-marker-vehicle',
})

interface DeliveryMapProps {
  destination: { latitude: number; longitude: number }
  currentPosition: { latitude: number; longitude: number } | null
  orderId: string
}

/** Centers map on destination once, then fits both markers once when first telemetry arrives. */
function InitialFit({ destination, currentPosition }: Omit<DeliveryMapProps, 'orderId'>) {
  const map = useMap()
  const fitted = useRef(false)

  useEffect(() => {
    if (fitted.current) return
    if (!currentPosition) return
    const bounds = L.latLngBounds(
      [currentPosition.latitude, currentPosition.longitude],
      [destination.latitude, destination.longitude],
    )
    map.fitBounds(bounds, { padding: [50, 50], maxZoom: 15 })
    fitted.current = true
    // Only run when currentPosition first becomes non-null
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentPosition])

  return null
}

/** Renders a Leaflet map showing vehicle position and delivery destination. */
export function DeliveryMap({ destination, currentPosition, orderId }: DeliveryMapProps) {
  const destLatLng = useMemo<[number, number]>(
    () => [destination.latitude, destination.longitude],
    [destination.latitude, destination.longitude],
  )

  const vehicleLatLng = useMemo<[number, number] | null>(
    () => currentPosition ? [currentPosition.latitude, currentPosition.longitude] : null,
    [currentPosition?.latitude, currentPosition?.longitude],
  )

  const routeLine = useMemo<[number, number][] | null>(
    () => vehicleLatLng ? [vehicleLatLng, destLatLng] : null,
    [vehicleLatLng, destLatLng],
  )

  return (
    <div className="rounded-lg border border-slate-700 overflow-hidden bg-slate-800/50">
      <div className="flex items-center justify-between border-b border-slate-700 bg-slate-800 px-4 py-2">
        <h2 className="text-xs font-medium uppercase tracking-wider text-slate-300">
          Live Tracking
        </h2>
        <span className="font-mono text-xs text-slate-500">{orderId.slice(0, 8)}…</span>
      </div>

      <div style={{ height: 320 }}>
        <MapContainer
          center={destLatLng}
          zoom={13}
          scrollWheelZoom
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            attribution='&copy; <a href="https://carto.com/">CARTO</a>'
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          />

          <InitialFit destination={destination} currentPosition={currentPosition} />

          <Marker position={destLatLng} icon={destinationIcon}>
            <Popup>
              <strong>Destination</strong>
              <br />
              {destination.latitude.toFixed(4)}, {destination.longitude.toFixed(4)}
            </Popup>
          </Marker>

          {vehicleLatLng && (
            <Marker position={vehicleLatLng} icon={vehicleIcon}>
              <Popup>
                <strong>Vehicle</strong>
                <br />
                {currentPosition!.latitude.toFixed(4)}, {currentPosition!.longitude.toFixed(4)}
              </Popup>
            </Marker>
          )}

          {routeLine && (
            <Polyline
              positions={routeLine}
              pathOptions={{ color: '#10b981', weight: 2, dashArray: '8 6', opacity: 0.7 }}
            />
          )}
        </MapContainer>
      </div>

      {!currentPosition && (
        <p className="px-4 py-2 text-xs text-slate-500">
          No telemetry yet — run the movement simulator to see live tracking.
        </p>
      )}
    </div>
  )
}
