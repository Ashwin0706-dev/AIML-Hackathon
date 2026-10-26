import { useMemo, useState } from 'react'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import Dashboard from './pages/Dashboard'
import EntityMatching from './pages/EntityMatching'
import CandidateExplorer from './pages/CandidateExplorer'
import ModelInsights from './pages/ModelInsights'
import Validation from './pages/Validation'
import DataExplorer from './pages/DataExplorer'
import FinalResults from './pages/FinalResults'
import Methodology from './pages/Methodology'

const pages = {
  dashboard: Dashboard,
  matching: EntityMatching,
  candidates: CandidateExplorer,
  model: ModelInsights,
  validation: Validation,
  data: DataExplorer,
  results: FinalResults,
  methodology: Methodology,
}

export default function App() {
  const [activePage, setActivePage] = useState('dashboard')
  const ActiveComponent = useMemo(() => pages[activePage] || Dashboard, [activePage])

  return (
    <div className="app-shell">
      <Sidebar activePage={activePage} setActivePage={setActivePage} />
      <div className="main-pane">
        <Header activePage={activePage} />
        <main className="page-content">
          <ActiveComponent />
        </main>
      </div>
    </div>
  )
}
