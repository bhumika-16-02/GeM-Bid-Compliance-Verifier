import { useState } from 'react'
import { DOC_TYPES, uploadBidderDocs } from '../api'
import FieldEditor from '../components/FieldEditor'

export default function BidderPage({ tender, onBidderReady }) {
  const [files, setFiles] = useState({})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [bidder, setBidder] = useState(null)

  if (!tender) {
    return <div className="card">Upload a tender first (Tender tab).</div>
  }

  async function handleUpload() {
    setLoading(true)
    setError('')
    try {
      setBidder(await uploadBidderDocs(files, tender.tender_id))
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  function updateDoc(index, newDoc) {
    const documents = bidder.documents.map((d, i) => (i === index ? newDoc : d))
    setBidder({ ...bidder, documents })
  }

  return (
    <div>
      <div className="card">
        <h2>2. Upload Bidder Documents</h2>
        {DOC_TYPES.map(({ key, label }) => (
          <label key={key} className="field">
            <span>{label}</span>
            <input
              type="file"
              accept=".pdf,.png,.jpg,.jpeg"
              onChange={(e) => setFiles({ ...files, [key]: e.target.files[0] })}
            />
          </label>
        ))}
        <button
          onClick={handleUpload}
          disabled={loading || Object.keys(files).length === 0}
        >
          {loading ? 'Extracting fields…' : 'Upload & Extract'}
        </button>
        {error && <p className="error">{error}</p>}
      </div>

      {bidder && (
        <>
          <h2>Review extracted fields: {bidder.company_name}</h2>
          {bidder.documents.map((doc, i) => (
            <FieldEditor key={doc.doc_type} doc={doc} onChange={(d) => updateDoc(i, d)} />
          ))}
          <button className="primary" onClick={() => onBidderReady(bidder)}>
            Confirm fields &amp; run compliance check
          </button>
        </>
      )}
    </div>
  )
}