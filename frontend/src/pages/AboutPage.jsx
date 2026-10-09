const HOW = [
  { t: 'Upload the tender', d: 'The system reads the tender PDF and lists every requirement it must check.' },
  { t: 'Upload bidder documents', d: 'PAN, GST, Udyam, OEM authorization and local content. Review the extracted fields and correct any mistakes.' },
  { t: 'Review the report', d: 'See a pass, fail or review result for each requirement with its evidence, then approve, reject or override.' },
]

const SAFEGUARDS = [
  'The AI only recommends. The Procurement Officer makes every final decision.',
  'Each result shows the source document and the rule it was checked against.',
  'Low-confidence readings are marked for review instead of being passed silently.',
  'Corrections you make are saved before the score is calculated.',
  'A written reason is required to reject a bid or override the AI.',
]

export default function AboutPage({ onStart }) {
  return (
    <div>
      <section className="hero">
        <h2 className="hero-title">Check every bid against the tender, with the evidence beside each result.</h2>
        <p className="hero-sub">Manual bid screening is slow and hard to audit. This assistant reads the documents, applies the tender's rules, and leaves the decision with you.</p>
        <button className="cta" onClick={onStart}>Start verification</button>
      </section>

      <section className="about-section">
        <h2>How it works</h2>
        <ol className="steps-grid">
          {HOW.map((s, i) => (
            <li key={s.t} className="card">
              <span className="n">{i + 1}</span>
              <h3>{s.t}</h3>
              <p>{s.d}</p>
            </li>
          ))}
        </ol>
      </section>

      <section className="about-section">
        <h2>Safeguards built in</h2>
        <ul className="checklist">
          {SAFEGUARDS.map((s) => <li key={s}>{s}</li>)}
        </ul>
      </section>
    </div>
  )
}