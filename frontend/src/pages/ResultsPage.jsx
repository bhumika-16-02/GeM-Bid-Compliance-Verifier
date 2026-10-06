import { useEffect, useState } from 'react'
import { getReport } from '../api'
import ScoreCard from '../components/ScoreCard'
import CheckTable from '../components/CheckTable'
import DecisionPanel from '../components/DecisionPanel'

export default function ResultsPage({ bidder }) {
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!bidder) return
    setLoading(true)
    setError('')
    getReport(bidder.bidder_id)
      .then(setReport)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [bidder])

  if (!bidder) return <div className="card">Complete the Bidder step first.</div>
  if (loading) return <div className="card">Running compliance checks…</div>
  if (error) return <div className="card error">{error}</div>
  if (!report) return null

  return (
    <div>
      <ScoreCard report={report} />
      <CheckTable checks={report.checks} />
      <DecisionPanel report={report} />
    </div>
  )
}