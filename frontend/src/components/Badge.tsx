import type { ReactNode } from 'react'

type BadgeProps = {
  tone: 'neutral' | 'low' | 'medium' | 'high' | 'active'
  children: ReactNode
}

function Badge({ tone, children }: BadgeProps) {
  return <span className={`badge badge-${tone}`}>{children}</span>
}

export default Badge
