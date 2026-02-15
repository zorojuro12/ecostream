import type { Order } from '../api/types'

interface OrderListProps {
  orders: Order[]
  /** When true, show a live-tracking pulse next to Distance when order has ETA */
  liveTracking?: boolean
  selectedOrderId: string | null
  onSelectOrder: (id: string) => void
}

export function OrderList({ orders, liveTracking = false, selectedOrderId, onSelectOrder }: OrderListProps) {
  if (orders.length === 0) {
    return (
      <p className="text-slate-400 text-sm py-8">No orders yet.</p>
    )
  }

  return (
    <div className="rounded-lg border border-slate-700 overflow-hidden bg-slate-800/50">
      <table className="w-full text-left">
        <thead>
          <tr className="border-b border-slate-700 bg-slate-800 text-slate-300 text-xs uppercase tracking-wider">
            <th className="px-4 py-3 font-medium">Order ID</th>
            <th className="px-4 py-3 font-medium">Status</th>
            <th className="px-4 py-3 font-medium">
              <span className="inline-flex items-center gap-1.5">
                Distance (km)
                {liveTracking && (
                  <span className="relative flex h-2 w-2" title="Live tracking">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-500 opacity-75" />
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-red-600" />
                  </span>
                )}
              </span>
            </th>
            <th className="px-4 py-3 font-medium">ETA (min)</th>
          </tr>
        </thead>
        <tbody>
          {orders.map((order) => (
            <tr
              key={order.id}
              role="button"
              tabIndex={0}
              onClick={() => onSelectOrder(order.id)}
              onKeyDown={(e) => e.key === 'Enter' && onSelectOrder(order.id)}
              className={`border-b border-slate-700/80 transition-colors cursor-pointer ${
                selectedOrderId === order.id ? 'bg-emerald-900/30' : 'hover:bg-slate-700/30'
              }`}
            >
              <td className="px-4 py-3 font-mono text-sm" data-testid="order-id">
                {order.id}
              </td>
              <td className="px-4 py-3" data-testid="order-status">
                <span className="inline-flex px-2 py-0.5 rounded text-xs font-medium bg-slate-600 text-slate-200">
                  {order.status}
                </span>
              </td>
              <td className="px-4 py-3 text-slate-300">
                {order.distanceKm != null ? order.distanceKm.toFixed(1) : '—'}
              </td>
              <td className="px-4 py-3" data-testid="order-eta">
                {order.estimatedArrivalMinutes != null
                  ? `${order.estimatedArrivalMinutes.toFixed(1)} min`
                  : '—'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
