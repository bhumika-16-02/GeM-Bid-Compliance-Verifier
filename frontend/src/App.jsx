import { useState } from 'react'
import UploadPage from './pages/UploadPage'
import BidderPage from './pages/BidderPage'
import ResultsPage from './pages/ResultsPage'
import { saveBidderFields } from './api'
import './App.css'

export default function App() {
  const [tab, setTab] = useState('tender')
  const [tender, setTender] = useState(null)
  const [bidder, setBidder] = useState(null)

  async function handleBidderReady(b) {
    await saveBidderFields(b)   // send the officer's corrections first
    setBidder(b)
    setTab('results')
  }

  return (
    <div className="app">
      <header>
        <h1>GeM Bid Compliance Verifier</h1>
        <p className="muted">AI recommends. The Procurement Officer decides.</p>
      </header>
      <nav>
        <button className={tab === 'tender' ? 'on' : ''} onClick={() => setTab('tender')}>Tender</button>
        <button className={tab === 'bidder' ? 'on' : ''} onClick={() => setTab('bidder')}>Bidder</button>
        <button className={tab === 'results' ? 'on' : ''} onClick={() => setTab('results')}>Results</button>
      </nav>
      {tab === 'tender' && <UploadPage onTenderReady={setTender} />}
      {tab === 'bidder' && <BidderPage tender={tender} onBidderReady={handleBidderReady} />}
      {tab === 'results' && <ResultsPage bidder={bidder} />}
    </div>
  )
}