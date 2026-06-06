import type { ReactNode } from 'react'

type Column<T> = {
  key: string
  title: string
  render: (row: T) => ReactNode
}

type PanelTableProps<T> = {
  title: string
  columns: Array<Column<T>>
  rows: T[]
}

function PanelTable<T>({ title, columns, rows }: PanelTableProps<T>) {
  return (
    <section className="card">
      <div className="panel-heading">
        <h3>{title}</h3>
      </div>

      <div className="table-wrapper">
        <table className="panel-table">
          <thead>
            <tr>
              {columns.map((column) => (
                <th key={column.key}>{column.title}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, index) => (
              <tr key={index}>
                {columns.map((column) => (
                  <td key={column.key}>{column.render(row)}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}

export default PanelTable
