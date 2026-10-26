import MatchBadge from './MatchBadge'

export default function CandidateTable({ rows = [] }) {
  if (!rows.length) {
    return <p className="empty-state">No candidate pairs available.</p>
  }

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Source 1</th>
            <th>Candidate</th>
            <th>Score</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row, idx) => (
            <tr key={idx}>
              <td>{row.source1_entity_id}</td>
              <td>{row.matched_entity_id}</td>
              <td>{Number(row.score || 0).toFixed(3)}</td>
              <td><MatchBadge status={row.decision || 'Match'} /></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
