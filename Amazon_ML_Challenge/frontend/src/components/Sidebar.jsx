export default function Sidebar({ activePage, setActivePage }) {
  const links = [
    { key: 'dashboard', label: 'Dashboard', icon: '📊' },
    { key: 'matching', label: 'Entity Matching', icon: '🔍' },
    { key: 'candidates', label: 'Candidate Explorer', icon: '🎯' },
    { key: 'model', label: 'Model Insights', icon: '🧠' },
    { key: 'validation', label: 'Validation', icon: '⚖️' },
    { key: 'data', label: 'Data Explorer', icon: '📁' },
    { key: 'results', label: 'Final Results', icon: '🏆' },
    { key: 'methodology', label: 'Methodology', icon: '📐' },
  ]

  return (
    <aside className="sidebar">
      <div className="brand-block">
        <div className="logo-badge">AM</div>
        <div className="brand-info">
          <h2>Amazon ML 2026</h2>
          <p>Entity Resolution</p>
        </div>
      </div>
      <nav className="nav-links">
        {links.map((item) => (
          <button
            key={item.key}
            className={`nav-link ${activePage === item.key ? 'active' : ''}`}
            onClick={() => setActivePage(item.key)}
          >
            <span>{item.icon}</span>
            <span>{item.label}</span>
          </button>
        ))}
      </nav>
      <div className="sidebar-footer">
        <span>System Status</span>
        <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span className="status-dot"></span> Online
        </span>
      </div>
    </aside>
  )
}
