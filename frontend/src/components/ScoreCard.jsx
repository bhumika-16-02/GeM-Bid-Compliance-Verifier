import { useEffect, useState } from 'react'

const R = 76
const C = 2 * Math.PI * R
const TICKS = 40

// counts a number up from 0 (jumps straight to the target if motion is reduced)
function useCountUp(target, ms = 1700, delay = 300) {
  const [v, setV] = useState(0)
  useEffect(() => {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      setV(target)
      return
    }
    let raf
    let start = null
    const tick = (t) => {
      if (start === null) start = t
      const p = Math.min((t - start) / ms, 1)
      setV(Math.round(target * (1 - Math.pow(1 - p, 3))))
      if (p < 1) raf = requestAnimationFrame(tick)
    }
    const timer = setTimeout(() => { raf = requestAnimationFrame(tick) }, delay)
    return () => { clearTimeout(timer); cancelAnimationFrame(raf) }
  }, [target, ms, delay])
  return v
}

export default function ScoreCard({ report }) {
  const score = Math.max(0, Math.min(100, Number(report.score) || 0))
  const checks = report.checks || []
  const total = checks.length || 1
  const count = (s) => checks.filter((c) => c.status === s).length
  const stats = [
    { key: 'pass', label: 'Passed', n: count('PASS'), color: 'var(--green)' },
    { key: 'review', label: 'Needs review', n: count('REVIEW'), color: 'var(--amber)' },
    { key: 'fail', label: 'Failed', n: count('FAIL'), color: 'var(--red)' },
  ]

  const shown = useCountUp(score)
  const nPass = useCountUp(stats[0].n, 1200, 1000)
  const nReview = useCountUp(stats[1].n, 1200, 1100)
  const nFail = useCountUp(stats[2].n, 1200, 1200)
  const animated = [nPass, nReview, nFail]

  const [ready, setReady] = useState(false)
  useEffect(() => {
    const id = requestAnimationFrame(() => setReady(true))
    return () => cancelAnimationFrame(id)
  }, [])

  return (
    <div className={`card score-card tone-${report.risk.toLowerCase()}`}>
      <div className="gauge" role="img" aria-label={`Compliance score ${score} percent`}>
        <svg viewBox="0 0 208 208" aria-hidden="true">
          <defs>
            <linearGradient id="gaugeGrad" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0" style={{ stopColor: 'var(--tone-a)' }} />
              <stop offset="1" style={{ stopColor: 'var(--tone)' }} />
            </linearGradient>
          </defs>
          {Array.from({ length: TICKS }, (_, i) => {
            const a = ((i / TICKS) * 360 - 90) * (Math.PI / 180)
            const lit = (i / TICKS) * 100 < shown
            return (
              <line
                key={i}
                className={lit ? 'g-tick lit' : 'g-tick'}
                x1={104 + 90 * Math.cos(a)} y1={104 + 90 * Math.sin(a)}
                x2={104 + 98 * Math.cos(a)} y2={104 + 98 * Math.sin(a)}
              />
            )
          })}
          <circle className="g-track" cx="104" cy="104" r={R} />
          <circle
            className="g-bar" cx="104" cy="104" r={R}
            transform="rotate(-90 104 104)"
            style={{ '--c': C, '--off': C * (1 - score / 100) }}
          />
        </svg>
        <div className="gauge-value">
          <span className="gauge-num">{shown}<small>%</small></span>
          <span className="gauge-label">compliance</span>
        </div>
      </div>

      <div className="score-main">
        <h2>Compliance score</h2>
        <div className="verdict">
          <span className="risk">{report.risk} risk</span>
          <span className="muted">AI recommendation: <b>{report.recommendation}</b></span>
        </div>
        <p className="summary">{report.summary}</p>

        <div className="breakdown" aria-hidden="true">
          {stats.map((s) => (
            <div key={s.key} className={`bd-seg bd-${s.key}`} style={{ width: ready ? `${(s.n / total) * 100}%` : 0 }} />
          ))}
        </div>
        <div className="stats">
          {stats.map((s, i) => (
            <div key={s.key} className="stat" style={{ '--c': s.color, '--i': i }}>
              <b>{animated[i]}</b>
              <span>{s.label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}