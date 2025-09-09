import React from 'react'

export default function TicketTable({tickets, refresh}){
  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold">Incoming Tickets</h2>
        <div>
          <button className="px-3 py-1 bg-indigo-600 text-white rounded mr-2" onClick={refresh}>Refresh</button>
        </div>
      </div>
      <table className="w-full text-sm">
        <thead className="text-left text-gray-500">
          <tr>
            <th>ID</th><th>Channel</th><th>Priority</th><th>Intent</th><th>Sentiment</th><th>Compliance</th><th>Created</th>
          </tr>
        </thead>
        <tbody>
          {tickets.map(t=>(
            <tr key={t.id} className="border-t">
              <td className="py-2">{t.id}</td>
              <td>{t.channel}</td>
              <td><span className={`px-2 py-0.5 rounded ${t.priority==='P1' ? 'bg-red-200 text-red-800' : t.priority==='P2' ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'}`}>{t.priority}</span></td>
              <td>{t.intent}</td>
              <td>{t.sentiment}</td>
              <td>{t.compliance_flag ? "⚠️" : "OK"}</td>
              <td>{new Date(t.created_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
