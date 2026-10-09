export default function ScoreCard({ report }) {
  return (
    <div className="card score-card">
      <div
        className="score-ring"
        style={{ '--score': report.score }}
        role="img"
        aria-label={`Compliance score ${report.score} percent`}
      >
        <span>{report.score}%</span>
      </div>
      <div>
        <h2>Compliance score</h2>
        <span className={`risk risk-${report.risk.toLowerCase()}`}>{report.risk} risk</span>
        <p className="muted">AI recommendation: <b>{report.recommendation}</b></p>
        <p>{report.summary}</p>
      </div>
    </div>
  )
}