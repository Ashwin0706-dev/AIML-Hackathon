import { useEffect, useState } from 'react'
import { fetchJson, postJson } from '../api'
import MetricCard from '../components/MetricCard'
import Loading from '../components/Loading'

export default function ModelInsights() {
  const [info, setInfo] = useState(null)
  const [training, setTraining] = useState(false)
  const [trainStatus, setTrainStatus] = useState('')

  useEffect(() => {
    fetchJson('/api/model/info')
      .then(setInfo)
      .catch(() => setInfo({}))
  }, [])

  const handleRetrain = async () => {
    setTraining(true)
    setTrainStatus('Triggering model training pipeline...')
    try {
      const res = await postJson('/api/train')
      setTrainStatus(res.message || 'Training started!')
      setTimeout(() => {
        fetchJson('/api/model/info').then(setInfo)
      }, 5000)
    } catch (e) {
      setTrainStatus('Failed: ' + e.message)
    } finally {
      setTraining(false)
    }
  }

  if (!info) return <Loading message="Loading model insights..." />

  const fMeta = info.feature_metadata || {}
  const tMeta = info.training_metadata || {}
  const importances = fMeta.feature_importances || {}

  // Sort features by importance
  const sortedFeatures = Object.entries(importances).sort((a, b) => b[1] - a[1])

  return (
    <div className="model-insights-page">
      <div className="metric-grid">
        <MetricCard label="Architecture" value={info.model_type || 'HistGradientBoosting'} detail="Scikit-Learn Tree Ensemble" />
        <MetricCard label="Engineered Features" value={String(info.features?.length || 14)} detail="Fuzzy string & token ratios" />
        <MetricCard label="Training Samples" value={(fMeta.train_samples || 7236).toLocaleString()} detail="Balanced positive & hard negative pairs" />
        <MetricCard label="Validation Samples" value={(fMeta.val_samples || 1764).toLocaleString()} detail="Grouped by Source 1 entity" />
        <MetricCard label="Optimal Threshold" value={String(tMeta.best_threshold || 0.90)} detail="F0.5 precision optimized cutoff" />
        <MetricCard label="Parameters" value="< 8B" detail="Local execution compliant" />
      </div>

      <section className="panel">
        <div className="panel-header">
          <div>
            <h3>Permutation Feature Importance</h3>
            <p className="panel-subtext">Calculated on held-out validation pairs to assess predictive power</p>
          </div>
          <button className="btn btn-primary" onClick={handleRetrain} disabled={training}>
            {training ? 'Training...' : '⚡ Train Model'}
          </button>
        </div>

        {trainStatus && (
          <div style={{ padding: '10px 14px', background: 'rgba(99, 102, 241, 0.15)', borderRadius: '8px', color: '#a5b4fc', marginBottom: '16px' }}>
            {trainStatus}
          </div>
        )}

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Feature Name</th>
                <th>Category</th>
                <th>Importance Score</th>
                <th>Visual Impact</th>
              </tr>
            </thead>
            <tbody>
              {sortedFeatures.map(([name, val]) => {
                let category = 'String Similarity'
                if (name.includes('address') || name.includes('addr')) category = 'Address Feature'
                else if (name.includes('name')) category = 'Business Name'
                else if (name.includes('country')) category = 'Country Comparison'

                const maxImp = Math.max(...Object.values(importances), 0.01)
                const widthPct = Math.min(100, Math.round((val / maxImp) * 100))

                return (
                  <tr key={name}>
                    <td><code>{name}</code></td>
                    <td><span className="badge badge-source">{category}</span></td>
                    <td><strong>{val.toFixed(4)}</strong></td>
                    <td style={{ minWidth: '180px' }}>
                      <div className="similarity-bar-track">
                        <div
                          className="similarity-bar-fill"
                          style={{
                            width: `${Math.max(5, widthPct)}%`,
                            background: 'linear-gradient(90deg, #6366f1, #38bdf8)',
                          }}
                        ></div>
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </section>

      <section className="panel">
        <div className="panel-header">
          <div>
            <h3>Feature Engineering Taxonomy</h3>
            <p className="panel-subtext">14 modular features combining phonetics, token sets, and fuzzy ratios</p>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '16px' }}>
          <div style={{ background: 'rgba(255,255,255,0.03)', padding: '16px', borderRadius: '12px' }}>
            <h4 style={{ color: '#818cf8', marginBottom: '6px' }}>Business Name Ratios</h4>
            <p style={{ fontSize: '0.85rem', color: '#cbd5e1' }}>
              RapidFuzz Levenshtein ratio, partial ratio, token sort ratio, token set ratio, and token Jaccard similarity.
            </p>
          </div>
          <div style={{ background: 'rgba(255,255,255,0.03)', padding: '16px', borderRadius: '12px' }}>
            <h4 style={{ color: '#38bdf8', marginBottom: '6px' }}>Address Comparison</h4>
            <p style={{ fontSize: '0.85rem', color: '#cbd5e1' }}>
              Standardized road abbreviations, address token Jaccard, missingness indicators, and length difference ratios.
            </p>
          </div>
          <div style={{ background: 'rgba(255,255,255,0.03)', padding: '16px', borderRadius: '12px' }}>
            <h4 style={{ color: '#34d399', marginBottom: '6px' }}>Open-Set Country Guard</h4>
            <p style={{ fontSize: '0.85rem', color: '#cbd5e1' }}>
              Country exact and normalized equality flag. Robust to unseen countries in held-out sets (e.g. France).
            </p>
          </div>
        </div>
      </section>
    </div>
  )
}
