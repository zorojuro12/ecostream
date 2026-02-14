import { useState, useEffect, useCallback } from 'react'
import { fetchOrders } from './api/orderClient'
import { OrderList } from './components/OrderList'
import type { Order } from './api/types'
import './App.css'

function App() {
  const [orders, setOrders] = useState<Order[]>([])

  const loadOrders = useCallback(() => {
    fetchOrders()
      .then(setOrders)
      .catch(() => setOrders([]))
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
            className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium transition-colors"
          >
            Refresh
          </button>
        </div>
        <OrderList orders={orders} />
      </div>
    </main>
  )
}

export default App
