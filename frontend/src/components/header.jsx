export default function Header({ tab, onNavigate }) {
  const verifying = tab !== 'about'
  const setSize = (px) => { document.documentElement.style.fontSize = px + 'px' }

  return (
    <>
      <a className="skip" href="#main">Skip to main content</a>
      <div className="flagstrip" aria-hidden="true"><i /><i /><i /></div>
      <div className="utility">
        <div className="wrap utility-row">
          <span>Public procurement compliance assistant (prototype)</span>
          <span className="textsize" role="group" aria-label="Text size">
            <button onClick={() => setSize(14)} aria-label="Smaller text">A-</button>
            <button onClick={() => setSize(16)} aria-label="Default text size">A</button>
            <button onClick={() => setSize(18)} aria-label="Larger text">A+</button>
          </span>
        </div>
      </div>
      <header className="masthead">
        <div className="wrap masthead-row">
          <svg className="seal" viewBox="0 0 48 48" aria-hidden="true">
            <path d="M24 3 42 10v13c0 11-8 19-18 22C14 42 6 34 6 23V10z" fill="#13294b" />
            <path d="M24 8 38 13v10c0 8.500-6 15-14 18-8-3-14-9.500-14-18V13z" fill="none" stroke="#d9730d" strokeWidth="1.500" />
            <path d="m16 24 6 6 11-12" fill="none" stroke="#fff" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          <div>
            <h1 className="site-title">GeM Bid Compliance Verifier</h1>
            <p className="tagline">AI recommends. The Procurement Officer decides.</p>
          </div>
        </div>
      </header>
      <nav className="mainnav" aria-label="Main">
        <div className="wrap">
          <button className={!verifying ? 'on' : ''} onClick={() => onNavigate('about')}>About</button>
          <button className={verifying ? 'on' : ''} onClick={() => onNavigate('tender')}>Verify a bid</button>
        </div>
      </nav>
    </>
  )
}