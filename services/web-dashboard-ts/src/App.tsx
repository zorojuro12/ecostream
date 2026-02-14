import { useState, useEffect } from 'react'
import { fetchOrders } from './api/orderClient'
import { OrderList } from './components/OrderList'
import type { Order } from './api/types'
import './App.css'

function App() {
  const [orders, setOrders] = useState<Order[]>([])

  useEffect(() => {
    fetchOrders()
      .then(setOrders)
      .catch(() => setOrders([]))
  }, [])

  return (
    <main>
      <h1>EcoStream Orders</h1>
      <OrderList orders={orders} />
    </main>
  )
}

export default App
