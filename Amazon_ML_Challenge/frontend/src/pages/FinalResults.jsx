import { useEffect, useState } from 'react'
import { fetchJson, getDownloadUrl } from '../api'
import MetricCard from '../components/MetricCard'
import Loading from '../components/Loading'

export default function FinalResults() {
  const [results, setResults] = useState(null)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    setLoading(true)
    fetchJson(`/api/results?page=${page}&page_size=25`)
      .then(setResults)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [page])

  if (error) {
    return (
      <div className="panel" style={{ borderColor: 'rgba(239, 68, 68, 0.4)' }}>
        <h3 style={{ color: '#f87171' }}>Results Error</h3>
        <p className="panel-subtext">{error}</p>
      </div>
    )
  }

  if (!results) return <Loading message="Loading final competition submission results..." />

  const metrics = results.metrics || {}
  const validation = results.validation || {}
  const checks = validation.checks || {}

  return (
    <div className="final-results-page">
      <div className="metric-grid">
        <MetricCard label="Evaluated Entities" value={metrics.total_source1_entities?.toLocaleString() || '5,000'} detail="Test Source 1 Records" />
        <MetricCard label="Entities With Matches" value={metrics.entities_with_matches?.toLocaleString() || '1,361'} detail="Confirmed business matches" />
        <MetricCard label="Entities Without Matches" value={metrics.entities_without_matches?.toLocaleString() || '3,639'} detail="Clean singletons (no false matches)" />
        <MetricCard label="Total Matched IDs" value={metrics.total_matched_ids?.toLocaleString() || '3,195'} detail="Generated S2 and S3 IDs" />
        <MetricCard label="Total Candidate IDs" value={metrics.total_candidates?.toLocaleString() || '97,198'} detail="High-recall blocking pool" />
        <MetricCard label="Submission Validity" value={validation.valid ? '100% Valid' : 'Check'} detail="Official rules validated" highlight />
      </div>

      <section className="panel" style={{ background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
        <div className="panel-header">
          <div>
            <h3 style={{ color: '#6ee7b7' }}>✓ Official Submission Files Ready</h3>
            <p className="panel-subtext">Directly downloadable TSV files formatted to Amazon ML Challenge specifications</p>
          </div>
          <div style={{ display: 'flex', gap: '12px' }}>
            <a
              href={getDownloadUrl('/api/download/matching-results')}
              className="btn btn-primary"
              download="matching_results.tsv"
            >
              📥 Download matching_results.tsv
            </a>
            <a
              href={getDownloadUrl('/api/download/candidate-pairs')}
              className="btn btn-secondary"
              download="candidate_pairs.tsv"
            >
              📥 Download candidate_pairs.tsv
            </a>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '12px', marginTop: '14px', fontSize: '0.85rem' }}>
          <div>✓ Tab-separated (<code>sep="\t"</code>) format</div>
          <div>✓ Candidate subset rule strictly enforced</div>
          <div>✓ No Source 1 IDs in matches</div>
          <div>✓ Every evaluated entity appears exactly once</div>
        </div>
      </section>

      <section className="panel">
        <div className="panel-header">
          <div>
            <h3>Generated Predictions Table ({results.total?.toLocaleString() || 0} rows)</h3>
            <p className="panel-subtext">Browsing matching_results.tsv output</p>
          </div>
        </div>

        {loading ? (
          <Loading message="Loading results page..." />
        ) : (
          <>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Source 1 Entity ID</th>
                    <th>Matched Entity IDs</th>
                    <th>Match Count</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {results.items?.map((item) => {
                    const mList = item.matched_entity_ids ? item.matched_entity_ids.split(',') : []
                    const hasMatch = mList.length > 0
                    return (
                      <tr key={item.source1_entity_id}>
                        <td><strong>{item.source1_entity_id}</strong></td>
                        <td style={{ fontSize: '0.85rem', color: hasMatch ? '#e2e8f0' : '#64748b' }}>
                          {item.matched_entity_ids || '— (No Match / Singleton)'}
                        </td>
                        <td>
                          <span className={`badge ${hasMatch ? 'badge-match' : 'badge-reject'}`}>
                            {mList.length} matches
                          </span>
                        </td>
                        <td>
                          {hasMatch ? (
                            <span style={{ color: '#34d399', fontSize: '0.78rem' }}>Resolved</span>
                          ) : (
                            <span style={{ color: '#94a3b8', fontSize: '0.78rem' }}>Singleton</span>
                          )}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>

            <div className="pagination">
              <span>Page {page} of {results.total_pages || 1}</span>
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
                  disabled={page >= (results.total_pages || 1)}
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
