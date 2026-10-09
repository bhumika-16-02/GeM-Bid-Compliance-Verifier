import { useState } from 'react'
import { uploadTender } from '../api'
import RequirementsList from '../components/RequirementsList'

export default function UploadPage({ onTenderReady }) {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [tender, setTender] = useState(null)

  async function handleUpload() {
    if (!file) return
    setLoading(true)
    setError('')
    try {
      const data = await uploadTender(file)
      setTender(data)
      onTenderReady?.(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div className="card">
        <h2>1. Upload Tender Document</h2>
        <input
          type="file"
          accept=".pdf"
          onChange={(e) => setFile(e.target.files[0])}
        />
        <button onClick={handleUpload} disabled={!file || loading}>
          {loading ? 'Extracting requirements…' : 'Upload & Extract'}
        </button>
        {error && <p className="error">{error}</p>}
      </div>
      {tender && <RequirementsList tender={tender} />}
    </div>
  )
}