import React from 'react'

export default function Dashboard({tickets}){
  const total = tickets.length
  const p1 = tickets.filter(t=>t.priority==='P1').length
  const compliance = tickets.filter(t=>t.compliance_flag).length
  return (
    <div className="bg-white p-4 rounded shadow space-y-4">
      <h3 className="text-lg font-semibold">Supervisor Dashboard</h3>
      <div className="grid grid-cols-1 gap-3">
        <div className="p-3 border rounded">
          <div className="text-sm text-gray-500">Total active tickets</div>
          <div className="text-2xl font-bold">{total}</div>
        </div>
        <div className="p-3 border rounded">
          <div className="text-sm text-gray-500">P1 (Critical)</div>
          <div className="text-2xl font-bold text-red-600">{p1}</div>
        </div>
        <div className="p-3 border rounded">
          <div className="text-sm text-gray-500">Compliance alerts</div>
          <div className="text-2xl font-bold">{compliance}</div>
        </div>
      </div>
    </div>
  )
}
