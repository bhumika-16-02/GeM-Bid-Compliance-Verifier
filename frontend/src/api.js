import tenderMock from './mock/tender.json'
import bidderMock from './mock/bidder.json'
import reportMock from './mock/report.json'

// Save the officer's corrections before running the check
export async function saveBidderFields(bidder) {
  if (USE_MOCK) {
    await wait(300)
    return { ok: true }
  }
  const res = await fetch(`/api/bidder/${bidder.bidder_id}/fields`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ documents: bidder.documents }),
  })
  if (!res.ok) throw new Error(`Saving fields failed (${res.status})`)
  return res.json()
}

export async function getReport(bidderId) {
  if (USE_MOCK) {
    await wait(1200)
    return reportMock
  }
  const res = await fetch(`/api/report/${bidderId}`)
  if (!res.ok) throw new Error(`Could not load report (${res.status})`)
  return res.json()
}

// decision: 'APPROVE' | 'REJECT' | 'OVERRIDE'
export async function submitDecision(bidderId, decision, reason) {
  if (USE_MOCK) {
    await wait(500)
    return { ok: true, decision, reason, decided_at: new Date().toISOString() }
  }
  const res = await fetch('/api/decision', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ bidder_id: bidderId, decision, reason }),
  })
  if (!res.ok) throw new Error(`Decision failed (${res.status})`)
  return res.json()
}

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