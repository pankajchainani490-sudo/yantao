import type { ReactNode } from 'react'

type DataStateProps = {
  loading?: boolean
  error?: string | null
  empty?: boolean
  emptyMessage?: string
  children: ReactNode
}

function DataState({ loading, error, empty, emptyMessage, children }: DataStateProps) {
  if (loading) {
    return <section className="card panel-state">正在加载...</section>
  }

  if (error) {
    return <section className="card panel-state panel-error">{error}</section>
  }

  if (empty) {
    return <section className="card panel-state">{emptyMessage ?? '暂无数据。'}</section>
  }

  return <>{children}</>
}

export default DataState
