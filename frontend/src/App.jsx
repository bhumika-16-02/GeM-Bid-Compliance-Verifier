import { useState } from 'react'
import UploadPage from './pages/UploadPage'
import './App.css'

export default function App() {
  const [tab, setTab] = useState('tender')
  const [tender, setTender] = useState(null)

  return (
    <div className="app">
      <header>
        <h1>GeM Bid Compliance Verifier</h1>
        <p className="muted">
          AI recommends. The Procurement Officer decides.
        </p>
      </header>
      <nav>
        <button
          className={tab === 'tender' ? 'on' : ''}
          onClick={() => setTab('tender')}
        >
          Tender
        </button>
        {/* Bidder / Results / Audit tabs come in the next batch */}
      </nav>
      {tab === 'tender' && <UploadPage onTenderReady={setTender} />}
    </div>
  )
}