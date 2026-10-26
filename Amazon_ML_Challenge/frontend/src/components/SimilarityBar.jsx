export default function SimilarityBar({ value }) {
  const num = typeof value === 'number' ? Math.max(0, Math.min(1, value)) : 0
  const pct = Math.round(num * 100)

  return (
    <div className="similarity-box">
      <div className="similarity-bar-track">
        <div className="similarity-bar-fill" style={{ width: `${pct}%` }}></div>
      </div>
      <span className="similarity-val">{pct}%</span>
    </div>
  )
}
