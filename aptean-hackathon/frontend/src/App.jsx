import React, {useEffect, useState} from 'react'
import axios from 'axios'
import TicketTable from './components/TicketTable'
import Dashboard from './components/Dashboard'

export default function App(){
  const [tickets, setTickets] = useState([])
  useEffect(()=>{ fetchTickets() }, [])
  async function fetchTickets(){
    try{
      const res = await axios.get('http://localhost:8000/tickets')
      setTickets(res.data)
    }catch(e){
      console.error(e)
    }
  }
  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <header className="max-w-6xl mx-auto mb-6">
        <h1 className="text-3xl font-extrabold">Aptean — AI Case Resolution Agent</h1>
        <p className="text-sm text-gray-600">Demo hackathon system — multi-channel ingestion, classification, RAG & audit</p>
      </header>
      <main className="max-w-6xl mx-auto grid grid-cols-12 gap-6">
        <section className="col-span-8 bg-white p-4 rounded shadow">
          <TicketTable tickets={tickets} refresh={fetchTickets}/>
        </section>
        <aside className="col-span-4">
          <Dashboard tickets={tickets}/>
        </aside>
      </main>
    </div>
  )
}
