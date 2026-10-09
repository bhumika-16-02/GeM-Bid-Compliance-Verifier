import { useState } from 'react'
import Header from './components/Header'
import Footer from './components/Footer'
import AboutPage from './pages/AboutPage'
import UploadPage from './pages/UploadPage'
import BidderPage from './pages/BidderPage'
import ResultsPage from './pages/ResultsPage'
import { saveBidderFields } from './api'
import './App.css'

const STEPS = [
  { key: 'tender', label: 'Tender document' },
  { key: 'bidder', label: 'Bidder documents' },
  { key: 'results', label: 'Compliance report' },
]

export default function App() {
  const [tab, setTab] = useState('about')
  const [tender, setTender] = useState(null)
  const [bidder, setBidder] = useState(null)
  const [error, setError] = useState('')

  async function handleBidderReady(b) {
    setError('')
    try {
      await saveBidderFields(b) // send the officer's corrections first
      setBidder(b)
      setTab('results')
    } catch (e) {
      setError(e.message)
    }
  }

  const unlocked = { tender: true, bidder: !!tender, results: !!bidder }

  return (
    <>
      <Header tab={tab} onNavigate={setTab} />
      <main id="main" className="page">
        <div className="wrap">
          {tab === 'about' ? (
            <AboutPage onStart={() => setTab('tender')} />
          ) : (
            <>
              <ol className="stepper" aria-label="Verification steps">
                {STEPS.map((s, i) => (
                  <li key={s.key}>
                    <button
                      className={tab === s.key ? 'step on' : unlocked[s.key] ? 'step' : 'step off'}
                      disabled={!unlocked[s.key]}
                      aria-current={tab === s.key ? 'step' : undefined}
                      onClick={() => setTab(s.key)}
                    >
                      <span className="n">{i + 1}</span>
                      {s.label}
                    </button>
                  </li>
                ))}
              </ol>
              {error && <p className="error" role="alert">{error}</p>}
              {tab === 'tender' && <UploadPage onTenderReady={setTender} />}
              {tab === 'bidder' && <BidderPage tender={tender} onBidderReady={handleBidderReady} />}
              {tab === 'results' && <ResultsPage bidder={bidder} />}
            </>
          )}
        </div>
      </main>
      <Footer onNavigate={setTab} />
    </>
  )
}