export default function MetricCard({ label, value, detail, highlight }) {
  return (
    <div className={`metric-card ${highlight ? 'highlight' : ''}`}>
      <span className="label">{label}</span>
      <strong className="value">{value}</strong>
      {detail && <small className="detail">{detail}</small>}
    </div>
  )
}
