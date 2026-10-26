import { useState } from 'react'
import { postJson } from '../api'

export default function Header({ activePage }) {
  const labels = {
    dashboard: 'Dataset & Pipeline Dashboard',
    matching: 'Interactive Entity Matching',
    candidates: 'Candidate & Blocking Explorer',
    model: 'ML Model Insights & Parameters',
    validation: 'F0.5 Precision Validation',
    data: 'Real Data Explorer',
    results: 'Official Submission Results',
    methodology: 'Engineering Methodology',
  }

  const [loading, setLoading] = useState(false)
  const [msg, setMsg] = useState('')

  const handleRetrain = async () => {
    setLoading(true)
    setMsg('Starting ML training...')
    try {
      const res = await postJson('/api/train')
      setMsg(res.message || 'Training triggered!')
      setTimeout(() => setMsg(''), 4000)
    } catch (e) {
      setMsg('Error: ' + e.message)
      setTimeout(() => setMsg(''), 4000)
    } finally {
      setLoading(false)
    }
  }

  return (
    <header className="topbar">
      <div>
        <span className="eyebrow">Business Entity Resolution • Official Challenge</span>
        <h1>{labels[activePage] || 'Dashboard'}</h1>
      </div>
      <div className="topbar-actions">
        {msg && <span style={{ fontSize: '0.85rem', color: '#34d399' }}>{msg}</span>}
        <button className="btn btn-secondary" onClick={handleRetrain} disabled={loading}>
          {loading ? 'Running...' : '⚡ Retrain Model'}
        </button>
      </div>
    </header>
  )
}
