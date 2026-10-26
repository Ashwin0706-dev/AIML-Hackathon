import { useEffect, useState } from 'react'
import { fetchJson } from '../api'
import Loading from '../components/Loading'

export default function CandidateExplorer() {
  const [data, setData] = useState(null)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(false)
  const [searchId, setSearchId] = useState('')
  const [singleCandidate, setSingleCandidate] = useState(null)
  const [singleLoading, setSingleLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    setLoading(true)
    fetchJson(`/api/candidate-pairs?page=${page}&page_size=20`)
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [page])

  const handleLookup = async () => {
    if (!searchId.trim()) return
    setSingleLoading(true)
    try {
      const res = await fetchJson(`/api/entity/${searchId.trim()}/candidates`)
      setSingleCandidate(res)
    } catch (e) {
      setSingleCandidate({ error: e.message || 'Entity not found' })
    } finally {
      setSingleLoading(false)
    }
  }

  return (
    <div className="candidate-explorer-page">
      <section className="panel">
        <div className="panel-header">
          <div>
            <h3>Candidate Blocking Explorer</h3>
            <p className="panel-subtext">Inspect high-recall blocking candidate sets for test entities</p>
          </div>
        </div>

        <div className="search-bar">
          <input
            className="input-field"
            style={{ minWidth: '320px', flex: 1 }}
            placeholder="Search candidate list for specific Source 1 ID (e.g. S1-714132312 or S1-965667)..."
            value={searchId}
            onChange={(e) => setSearchId(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleLookup()}
          />
          <button className="btn btn-primary" onClick={handleLookup} disabled={singleLoading}>
            {singleLoading ? 'Searching...' : 'Inspect Candidates'}
          </button>
        </div>

        {singleCandidate && (
          <div style={{ marginTop: '16px', padding: '16px', background: 'rgba(255,255,255,0.03)', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
            {singleCandidate.error ? (
              <span style={{ color: '#fca5a5' }}>{singleCandidate.error}</span>
            ) : (
              <div>
                <h4 style={{ color: '#818cf8', marginBottom: '8px' }}>
                  Entity {singleCandidate.entity_id} — {singleCandidate.candidate_count} Candidates Blocked
                </h4>
                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                  {singleCandidate.candidates?.map((c) => (
                    <span key={c.candidate_id} className="badge badge-source">
                      {c.candidate_id} ({c.decision})
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </section>

      <section className="panel">
        <div className="panel-header">
          <div>
            <h3>Official Candidate Pairs ({data?.total?.toLocaleString() || '5,000'} Generated)</h3>
            <p className="panel-subtext">Subset rule enforced: All matching results are strictly drawn from these candidates</p>
          </div>
        </div>

        {loading ? (
          <Loading message="Loading candidate pairs..." />
        ) : (
          <>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Source 1 Entity ID</th>
                    <th>Candidate Count</th>
                    <th>Candidate Entity IDs (Sample)</th>
                  </tr>
                </thead>
                <tbody>
                  {data?.items?.map((item) => {
                    const cands = item.candidate_entity_ids ? item.candidate_entity_ids.split(',') : []
                    return (
                      <tr key={item.source1_entity_id}>
                        <td><strong>{item.source1_entity_id}</strong></td>
                        <td>
                          <span className="badge badge-match">{cands.length} candidates</span>
                        </td>
                        <td style={{ fontSize: '0.8rem', color: '#cbd5e1' }}>
                          {cands.slice(0, 6).join(', ')}
                          {cands.length > 6 && <span style={{ color: '#94a3b8' }}> + {cands.length - 6} more</span>}
                          {cands.length === 0 && <span style={{ color: '#64748b' }}>None</span>}
                        </td>
                      </tr>
                    )
                  })}
                  {(!data?.items || data.items.length === 0) && (
                    <tr>
                      <td colSpan="3" style={{ textAlign: 'center', padding: '30px', color: '#94a3b8' }}>
                        No candidate pairs generated yet. Run test prediction to generate candidate_pairs.tsv.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            <div className="pagination">
              <span>Page {page} of {data?.total_pages || 1}</span>
              <div className="pagination-controls">
                <button
                  className="btn btn-secondary"
                  disabled={page <= 1}
                  onClick={() => setPage((p) => p - 1)}
                >
                  ← Previous
                </button>
                <button
                  className="btn btn-secondary"
                  disabled={page >= (data?.total_pages || 1)}
                  onClick={() => setPage((p) => p + 1)}
                >
                  Next →
                </button>
              </div>
            </div>
          </>
        )}
      </section>
    </div>
  )
}
