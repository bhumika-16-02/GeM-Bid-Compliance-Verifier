import tenderMock from './mock/tender.json'

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