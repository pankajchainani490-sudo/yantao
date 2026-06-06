type StatCardProps = {
  title: string
  value: string
  hint: string
}

function StatCard({ title, value, hint }: StatCardProps) {
  return (
    <section className="card stat-card">
      <p className="card-label">{title}</p>
      <strong className="card-value">{value}</strong>
      <p className="card-hint">{hint}</p>
    </section>
  )
}

export default StatCard
