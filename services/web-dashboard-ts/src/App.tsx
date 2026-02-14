import { useState, useEffect, useCallback } from 'react'
import { fetchOrders } from './api/orderClient'
import { OrderList } from './components/OrderList'
import type { Order } from './api/types'
import './App.css'

type FetchState = 'idle' | 'loading' | 'success' | 'error'

function App() {
  const [orders, setOrders] = useState<Order[]>([])
  const [fetchState, setFetchState] = useState<FetchState>('idle')
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  const loadOrders = useCallback(() => {
    setFetchState('loading')
    setErrorMessage(null)
    fetchOrders()
      .then((data) => {
        setOrders(data)
        setFetchState('success')
      })
      .catch((err) => {
        setOrders([])
        setFetchState('error')
        setErrorMessage(err instanceof Error ? err.message : 'Failed to load orders')
      })
  }, [])

  useEffect(() => {
    loadOrders()
  }, [loadOrders])

  return (
    <main className="min-h-screen bg-slate-900 text-slate-100 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-semibold text-slate-100 tracking-tight">
            EcoStream Orders
          </h1>
          <button
            type="button"
            onClick={loadOrders}
            disabled={fetchState === 'loading'}
            className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium transition-colors"
          >
            {fetchState === 'loading' ? 'Loading…' : 'Refresh'}
          </button>
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
          <OrderList orders={orders} />
        )}
      </div>
    </main>
  )
}

export default App
