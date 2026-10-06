import { useState } from 'react'

export default function CheckTable({ checks }) {
  const [open, setOpen] = useState(null)

  return (
    <div className="card">
      <h2>Requirement checks</h2>
      {checks.map((c) => (
        <div key={c.requirement_id} className="check-row">
          <div
            className="check-main"
            onClick={() => setOpen(open === c.requirement_id ? null : c.requirement_id)}
          >
            <span className={`status status-${c.status.toLowerCase()}`}>{c.status}</span>
            <span>{c.requirement}</span>
            <span className="muted chevron">{open === c.requirement_id ? '▲' : '▼'}</span>
          </div>
          {open === c.requirement_id && (
            <div className="check-detail">
              <p>{c.evidence}</p>
              <p className="muted">Source: {c.source} · Rule: {c.rule}</p>
            </div>
          )}
        </div>
      ))}
    </div>
  )
}