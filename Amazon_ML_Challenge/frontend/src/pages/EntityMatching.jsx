import { useState } from 'react'
import { fetchJson } from '../api'
import MatchBadge from '../components/MatchBadge'
import SimilarityBar from '../components/SimilarityBar'
import Loading from '../components/Loading'

export default function EntityMatching() {
  const [entityId, setEntityId] = useState('S1-965667')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const sampleIds = [
    'S1-965667',
    'S1-102811957',
    'S1-343815751',
    'S1-656753428',
    'S1-55344266',
    'S1-925783039',
  ]

  const handleSearch = async (idToSearch) => {
    const id = (idToSearch || entityId).trim()
    if (!id) return

    setLoading(true)
    setError('')
    try {
      const data = await fetchJson(`/api/entity/${id}/matches`)
      setResult(data)
    } catch (e) {
      setError(e.message || 'Entity not found')
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="entity-matching-page">
      <section className="panel">
        <div className="panel-header">
          <div>
            <h3>Interactive Business Entity Resolution</h3>
            <p className="panel-subtext">Look up any Source 1 business to evaluate candidate matches and ML confidence</p>
          </div>
        </div>

        <div className="chips-row">
          <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Try real sample entities:</span>
          {sampleIds.map((sid) => (
            <button
              key={sid}
              className="chip-btn"
              onClick={() => {
                setEntityId(sid)
                handleSearch(sid)
              }}
            >
              {sid}
            </button>
          ))}
        </div>

        <div className="search-bar" style={{ marginTop: '16px' }}>
          <input
            className="input-field"
            style={{ minWidth: '320px', flex: 1 }}
            value={entityId}
            onChange={(e) => setEntityId(e.target.value)}
            placeholder="Enter Source 1 Entity ID (e.g. S1-965667)..."
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button className="btn btn-primary" onClick={() => handleSearch()} disabled={loading}>
            {loading ? 'Searching...' : '🔍 Find Matches'}
          </button>
        </div>

        {error && (
          <div style={{ padding: '12px 16px', background: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '8px', color: '#fca5a5', marginTop: '12px' }}>
            {error}
          </div>
        )}
      </section>

      {loading && <Loading message={`Generating candidates and scoring features for ${entityId}...`} />}

      {result && result.found && (
        <>
          <section className="panel" style={{ background: 'rgba(20, 30, 52, 0.95)', border: '1px solid rgba(99, 102, 241, 0.3)' }}>
            <div className="panel-header">
              <div>
                <span className="eyebrow">Reference Entity</span>
                <h3 style={{ fontSize: '1.3rem' }}>{result.source_entity?.business_name || '—'}</h3>
              </div>
              <span className="badge badge-source">{result.source_entity?.entity_id}</span>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginTop: '12px' }}>
              <div>
                <span style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase' }}>Address</span>
                <p style={{ fontWeight: '500', marginTop: '4px' }}>{result.source_entity?.business_address || '—'}</p>
              </div>
              <div>
                <span style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase' }}>Country</span>
                <p style={{ fontWeight: '600', color: '#38bdf8', marginTop: '4px' }}>{result.source_entity?.country || '—'}</p>
              </div>
              <div>
                <span style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase' }}>Ground Truth Benchmark</span>
                <p style={{ fontWeight: '500', marginTop: '4px', color: '#a7f3d0' }}>
                  {result.source_entity?.ground_truth_matches || 'Unmatched in GT / Held-out'}
                </p>
              </div>
            </div>
          </section>

          <section className="panel">
            <div className="panel-header">
              <div>
                <h3>Ranked Candidate Matches ({result.candidates_count})</h3>
                <p className="panel-subtext">
                  Cutoff threshold = <strong>{result.threshold}</strong> • {result.matched_count} matches approved
                </p>
              </div>
            </div>

            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Candidate ID</th>
                    <th>Source</th>
                    <th>Business Name</th>
                    <th>Address</th>
                    <th>Country</th>
                    <th>Name Sim</th>
                    <th>Addr Sim</th>
                    <th>Probability</th>
                    <th>Decision</th>
                  </tr>
                </thead>
                <tbody>
                  {result.candidates.map((cand) => (
                    <tr key={cand.candidate_id}>
                      <td><strong>{cand.candidate_id}</strong></td>
                      <td><span className="badge badge-source">{cand.candidate_source}</span></td>
                      <td>{cand.business_name}</td>
                      <td>{cand.business_address || <span style={{ color: '#64748b' }}>Missing</span>}</td>
                      <td>{cand.country}</td>
                      <td><SimilarityBar value={cand.name_similarity} /></td>
                      <td><SimilarityBar value={cand.address_similarity} /></td>
                      <td>
                        <strong style={{ color: cand.probability >= result.threshold ? '#34d399' : '#94a3b8' }}>
                          {(cand.probability * 100).toFixed(1)}%
                        </strong>
                      </td>
                      <td><MatchBadge decision={cand.decision} /></td>
                    </tr>
                  ))}
                  {result.candidates.length === 0 && (
                    <tr>
                      <td colSpan="9" style={{ textAlign: 'center', color: '#94a3b8', padding: '30px' }}>
                        No candidates found for this entity.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </section>
        </>
      )}
    </div>
  )
}
