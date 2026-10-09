import { useState } from 'react'

const ICON = { PASS: '\u2713', FAIL: '\u2715', REVIEW: '!' }

export default function CheckTable({ checks }) {
  const [open, setOpen] = useState(null)

  return (
    <div className="card">
      <h2>Requirement checks</h2>
      <div className="check-list">
        {checks.map((c, i) => {
          const isOpen = open === c.requirement_id
          const s = c.status.toLowerCase()
          return (
            <div
              key={c.requirement_id}
              className={`check-row row-${s}${isOpen ? ' open' : ''}`}
              style={{ '--i': i }}
            >
              <button
                className="check-main"
                aria-expanded={isOpen}
                onClick={() => setOpen(isOpen ? null : c.requirement_id)}
              >
                <span className={`status status-${s}`}>
                  <b aria-hidden="true">{ICON[c.status]}</b>
                  {c.status}
                </span>
                <span className="check-req">{c.requirement}</span>
                <span className="chevron" aria-hidden="true" />
              </button>
              {isOpen && (
                <div className="check-detail">
                  <p>{c.evidence}</p>
                  <p className="muted">Source: {c.source} &middot; Rule: {c.rule}</p>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}