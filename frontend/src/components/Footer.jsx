export default function Footer({ onNavigate }) {
  return (
    <footer className="site-footer">
      <div className="wrap foot-grid">
        <div>
          <h3>About this system</h3>
          <p>Checks bidder documents against tender requirements and shows the evidence for every result, so officers can decide faster and with a clear record.</p>
        </div>
        <div>
          <h3>Quick links</h3>
          <ul className="foot-links">
            <li><button onClick={() => onNavigate('about')}>About</button></li>
            <li><button onClick={() => onNavigate('tender')}>Verify a bid</button></li>
          </ul>
        </div>
        <div>
          <h3>Notice</h3>
          <p>Student hackathon prototype. It is not an official Government of India website, and its results are recommendations only. Debarment is checked against a sample list.</p>
        </div>
      </div>
      <div className="foot-bar">
        <div className="wrap">&copy; 2026 GeM Bid Compliance Verifier, prototype build</div>
      </div>
    </footer>
  )
}