import tenderMock from './mock/tender.json'
import bidderMock from './mock/bidder.json'

export const DOC_TYPES = [
  { key: 'PAN', label: 'PAN Card' },
  { key: 'GST', label: 'GST Certificate' },
  { key: 'UDYAM', label: 'Udyam Certificate' },
  { key: 'OEM', label: 'OEM Authorization' },
  { key: 'LOCAL_CONTENT', label: 'Local Content Declaration' },
]

// files = { PAN: File, GST: File, ... }
export async function uploadBidderDocs(files, tenderId) {
  if (USE_MOCK) {
    await wait(1000)
    return bidderMock
  }
  const form = new FormData()
  form.append('tender_id', tenderId)
  Object.entries(files).forEach(([type, file]) => form.append(type, file))
  const res = await fetch('/api/bidder/upload', { method: 'POST', body: form })
  if (!res.ok) throw new Error(`Bidder upload failed (${res.status})`)
  return res.json()
}

// true = use mock JSON, false = call B's real backend
export const USE_MOCK = true

const wait = (ms) => new Promise((r) => setTimeout(r, ms))

export async function uploadTender(file) {
  if (USE_MOCK) {
    await wait(800)
    return tenderMock
  }
  const form = new FormData()
  form.append('file', file)
  const res = await fetch('/api/tender/upload', { method: 'POST', body: form })
  if (!res.ok) throw new Error(`Upload failed (${res.status})`)
  return res.json()
}