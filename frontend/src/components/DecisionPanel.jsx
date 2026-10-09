import { useState } from 'react'
import { submitDecision } from '../api'

export default function DecisionPanel({ report, onDecided }) {
  const [reason, setReason] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [done, setDone] = useState(null)

  async function decide(decision) {
    if (decision !== 'APPROVE' && reason.trim().length < 5) {
      setError('Please give a reason (at least a few words) for reject or override.')
      return
    }
    setLoading(true)
    setError('')
    try {
      const res = await submitDecision(report.bidder_id, decision, reason.trim())
      setDone(res)
      onDecided?.(res)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  if (done) {
    return (
      <div className="card">
        <h2>Decision recorded</h2>
        <p><b>{done.decision}</b>{done.reason ? `: ${done.reason}` : ''}</p>
        <p className="muted">{new Date(done.decided_at).toLocaleString()}</p>
      </div>
    )
  }

  return (
    <div className="card">
      <h2>Procurement Officer decision</h2>
      <p className="muted">The AI only recommends. This decision is yours.</p>
      <textarea
        rows={3}
        placeholder="Reason (required for reject / override)"
        value={reason}
        onChange={(e) => setReason(e.target.value)}
      />
      <div className="decision-buttons">
        <button className="approve" disabled={loading} onClick={() => decide('APPROVE')}>Approve</button>
        <button className="reject" disabled={loading} onClick={() => decide('REJECT')}>Reject</button>
        <button className="override" disabled={loading} onClick={() => decide('OVERRIDE')}>Override AI</button>
      </div>
      {error && <p className="error">{error}</p>}
    </div>
  )
}