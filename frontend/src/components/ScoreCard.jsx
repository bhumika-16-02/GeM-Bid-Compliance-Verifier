export default function ScoreCard({ report }) {
  return (
    <div className="card score-card">
      <div className="score-circle">{report.score}%</div>
      <div>
        <h2>Compliance Score</h2>
        <span className={`risk risk-${report.risk.toLowerCase()}`}>
          {report.risk} RISK
        </span>
        <p className="muted">AI recommendation: <b>{report.recommendation}</b></p>
        <p>{report.summary}</p>
      </div>
    </div>
  )
}