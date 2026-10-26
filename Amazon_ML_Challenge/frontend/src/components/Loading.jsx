export default function Loading({ message = 'Loading challenge data...' }) {
  return (
    <div className="spinner-container">
      <div className="spinner"></div>
      <p style={{ fontSize: '0.9rem', color: '#94a3b8' }}>{message}</p>
    </div>
  )
}
