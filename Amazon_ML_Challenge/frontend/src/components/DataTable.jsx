export default function DataTable({ rows = [] }) {
  if (!rows.length) {
    return <p className="empty-state">No rows available.</p>
  }

  const columns = Object.keys(rows[0])

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column}>{column}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, idx) => (
            <tr key={idx}>
              {columns.map((column) => (
                <td key={`${idx}-${column}`}>{String(row[column])}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
