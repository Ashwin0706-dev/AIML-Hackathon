export const API_BASE = 'http://localhost:8000'

export async function fetchJson(url) {
  const res = await fetch(`${API_BASE}${url}`)
  if (!res.ok) {
    const errorText = await res.text().catch(() => '')
    throw new Error(`HTTP ${res.status}: ${errorText || res.statusText}`)
  }
  return res.json()
}

export async function postJson(url, data = {}) {
  const res = await fetch(`${API_BASE}${url}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!res.ok) {
    const errorText = await res.text().catch(() => '')
    throw new Error(`HTTP ${res.status}: ${errorText || res.statusText}`)
  }
  return res.json()
}

export function getDownloadUrl(url) {
  return `${API_BASE}${url}`
}
