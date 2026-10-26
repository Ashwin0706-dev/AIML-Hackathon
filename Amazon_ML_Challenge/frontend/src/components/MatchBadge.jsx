export default function MatchBadge({ decision }) {
  const isMatch = String(decision).toLowerCase() === 'match'
  return (
    <span className={`badge ${isMatch ? 'badge-match' : 'badge-reject'}`}>
      {isMatch ? '✓ Match' : '✗ Reject'}
    </span>
  )
}
