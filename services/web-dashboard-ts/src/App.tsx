import { useState, useEffect, useCallback, useRef } from 'react'
import { fetchOrders } from './api/orderClient'
import { OrderList } from './components/OrderList'
import { AssistantChat } from './components/AssistantChat'
import type { Order } from './api/types'
import './App.css'

const POLL_INTERVAL_MS = 5000

type FetchState = 'idle' | 'loading' | 'success' | 'error'

function App() {
  const [orders, setOrders] = useState<Order[]>([])
  const [fetchState, setFetchState] = useState<FetchState>('idle')
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [selectedOrderId, setSelectedOrderId] = useState<string | null>(null)
  const isMounted = useRef(true)

  const loadOrders = useCallback((showLoading = true) => {
    if (showLoading) {
      setFetchState('loading')
      setErrorMessage(null)
    }
    fetchOrders()
      .then((data) => {
        if (isMounted.current) {
          setOrders(data)
          setFetchState('success')
        }
      })
      .catch((err) => {
        if (isMounted.current) {
          if (showLoading) {
            setOrders([])
            setFetchState('error')
            setErrorMessage(err instanceof Error ? err.message : 'Failed to load orders')
          }
        }
      })
  }, [])

  useEffect(() => {
    isMounted.current = true
    loadOrders(true)
    return () => {
      isMounted.current = false
    }
  }, [loadOrders])

  useEffect(() => {
    if (!autoRefresh || fetchState !== 'success') return
    const id = setInterval(() => loadOrders(false), POLL_INTERVAL_MS)
    return () => clearInterval(id)
  }, [autoRefresh, fetchState, loadOrders])

  return (
    <main className="min-h-screen bg-slate-900 text-slate-100 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-semibold text-slate-100 tracking-tight">
            EcoStream Orders
          </h1>
          <div className="flex items-center gap-3">
            <label className="flex items-center gap-2 text-slate-300 text-sm cursor-pointer">
              <input
                type="checkbox"
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                className="rounded border-slate-600 bg-slate-800 text-emerald-600 focus:ring-emerald-500"
              />
              Auto-refresh (5s)
            </label>
            <button
              type="button"
              onClick={() => loadOrders(true)}
              disabled={fetchState === 'loading'}
              className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium transition-colors"
            >
              {fetchState === 'loading' ? 'Loading…' : 'Refresh'}
            </button>
          </div>
        </div>
        {fetchState === 'loading' && orders.length === 0 && (
          <p className="text-slate-400 py-8" role="status">Loading orders…</p>
        )}
        {fetchState === 'error' && (
          <div
            className="mb-4 p-4 rounded-lg bg-red-900/30 border border-red-700 text-red-200 text-sm"
            role="alert"
          >
            {errorMessage}
          </div>
        )}
        {(fetchState === 'success' || orders.length > 0) && (
          <OrderList
            orders={orders}
            liveTracking={autoRefresh && orders.some((o) => o.estimatedArrivalMinutes != null)}
            selectedOrderId={selectedOrderId}
            onSelectOrder={setSelectedOrderId}
          />
        )}
      </div>
      <AssistantChat selectedOrderId={selectedOrderId} />
    </main>
  )
}

export default App
