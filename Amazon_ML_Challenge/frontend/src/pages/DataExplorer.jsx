import { useEffect, useState } from 'react'
import { fetchJson } from '../api'
import Loading from '../components/Loading'

export default function DataExplorer() {
  const [source, setSource] = useState('source1')
  const [page, setPage] = useState(1)
  const [query, setQuery] = useState('')
  const [country, setCountry] = useState('')
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const loadData = () => {
    setLoading(true)
    setError('')
    const q = encodeURIComponent(query.trim())
    const c = encodeURIComponent(country.trim())
    fetchJson(`/api/data/${source}?page=${page}&page_size=20&query=${q}&country=${c}`)
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    loadData()
  }, [source, page, country])

  const handleSearchSubmit = (e) => {
    e.preventDefault()
    setPage(1)
    loadData()
  }

  return (
    <div className="data-explorer-page">
      <section className="panel">
        <div className="panel-header">
          <div>
            <h3>Challenge Data Explorer</h3>
            <p className="panel-subtext">Memory-safe paginated exploration of indexed challenge records</p>
          </div>
          <div style={{ display: 'flex', gap: '8px' }}>
            {['source1', 'source2', 'source3', 'ground_truth'].map((src) => (
              <button
                key={src}
                className={`btn ${source === src ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => {
                  setSource(src)
                  setPage(1)
                }}
              >
                {src.replace('_', ' ').toUpperCase()}
              </button>
            ))}
          </div>
        </div>

        <form className="search-bar" onSubmit={handleSearchSubmit}>
          <input
            className="input-field"
            style={{ flex: 1, minWidth: '220px' }}
            placeholder={`Filter ${source} by business name or ID...`}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          {source !== 'ground_truth' && (
            <select className="select-field" value={country} onChange={(e) => { setCountry(e.target.value); setPage(1); }}>
              <option value="">All Countries</option>
              <option value="US">United States (US)</option>
              <option value="India">India</option>
              <option value="France">France</option>
            </select>
          )}
          <button type="submit" className="btn btn-secondary">
            Filter
          </button>
        </form>

        {error && <div style={{ color: '#f87171', padding: '12px 0' }}>{error}</div>}

        {loading ? (
          <Loading message={`Querying ${source}...`} />
        ) : (
          <>
            <div className="table-wrap">
              <table>
                <thead>
                  {source === 'ground_truth' ? (
                    <tr>
                      <th>Source 1 Entity ID</th>
                      <th>Matched Entity IDs</th>
                      <th>Matches Count</th>
                    </tr>
                  ) : (
                    <tr>
                      <th>Entity ID</th>
                      <th>Source File</th>
                      <th>Business Name</th>
                      <th>Business Address</th>
                      <th>Country</th>
                    </tr>
                  )}
                </thead>
                <tbody>
                  {data?.items?.map((item, idx) => {
                    if (source === 'ground_truth') {
                      const mList = item.matched_entity_ids ? item.matched_entity_ids.split(',') : []
                      return (
                        <tr key={item.source1_entity_id || idx}>
                          <td><strong>{item.source1_entity_id}</strong></td>
                          <td style={{ fontSize: '0.82rem', color: '#cbd5e1' }}>
                            {item.matched_entity_ids || <span style={{ color: '#64748b' }}>Empty (no match)</span>}
                          </td>
                          <td>
                            <span className="badge badge-match">{mList.length} matches</span>
                          </td>
                        </tr>
                      )
                    }
                    return (
                      <tr key={item.entity_id || idx}>
                        <td><strong>{item.entity_id}</strong></td>
                        <td><span className="badge badge-source">{item.source}</span></td>
                        <td>{item.business_name}</td>
                        <td style={{ fontSize: '0.82rem', color: '#94a3b8' }}>{item.business_address || '—'}</td>
                        <td><span style={{ color: '#38bdf8', fontWeight: '600' }}>{item.country}</span></td>
                      </tr>
                    )
                  })}
                  {(!data?.items || data.items.length === 0) && (
                    <tr>
                      <td colSpan={source === 'ground_truth' ? 3 : 5} style={{ textAlign: 'center', padding: '30px', color: '#94a3b8' }}>
                        No records match the current filters.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            <div className="pagination">
              <span>Showing Page {page} of {data?.total_pages || 1} ({data?.total?.toLocaleString() || 0} total)</span>
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
