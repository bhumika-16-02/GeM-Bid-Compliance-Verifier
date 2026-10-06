export default function RequirementsList({ tender }) {
  return (
    <div className="card">
      <h2>{tender.title}</h2>
      <p className="muted">Tender ID: {tender.tender_id}</p>
      <ul className="req-list">
        {tender.requirements.map((r) => (
          <li key={r.id}>
            <span className="tag">{r.type}</span>
            <span>{r.text}</span>
            {r.mandatory && <span className="badge">Mandatory</span>}
          </li>
        ))}
      </ul>
    </div>
  )
}