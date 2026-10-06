export default function FieldEditor({ doc, onChange }) {
  const low = doc.confidence < 0.85

  function setField(name, value) {
    onChange({ ...doc, fields: { ...doc.fields, [name]: value } })
  }

  return (
    <div className="card">
      <div className="doc-head">
        <h3>{doc.doc_type}</h3>
        <span className={low ? 'badge' : 'badge ok'}>
          {low ? 'Low confidence – please verify' : 'Confident'} · {Math.round(doc.confidence * 100)}%
        </span>
      </div>
      <p className="muted">Source: {doc.source_file}</p>
      {Object.entries(doc.fields).map(([name, value]) => (
        <label key={name} className="field">
          <span>{name.replaceAll('_', ' ')}</span>
          <input value={value} onChange={(e) => setField(name, e.target.value)} />
        </label>
      ))}
    </div>
  )
}