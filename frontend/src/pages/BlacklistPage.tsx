import { useState } from 'react'

import Badge from '../components/Badge'
import DataState from '../components/DataState'
import PanelTable from '../components/PanelTable'
import { createBlacklistEntry, deleteBlacklistEntry, getBlacklist } from '../api/security'
import { useAsyncData } from '../hooks/useAsyncData'
import { usePageTitle } from '../hooks/usePageTitle'
import { formatReason, formatRiskLevel, formatStatus, formatTrafficLabel } from '../utils/i18n'
import { formatTimestamp } from '../utils/time'

function toBadgeTone(riskLevel: string): 'low' | 'medium' | 'high' | 'neutral' {
  if (riskLevel === 'low' || riskLevel === 'medium' || riskLevel === 'high') {
    return riskLevel
  }

  return 'neutral'
}

function BlacklistPage() {
  usePageTitle('黑名单')
  const blacklistState = useAsyncData(getBlacklist, [])
  const [submitting, setSubmitting] = useState(false)
  const [form, setForm] = useState({
    source_ip: '192.168.55.2',
    source_port: 4040,
    attack_type: 'trojan',
    risk_level: 'medium',
    reason: '前端联调期间手动复核。',
  })

  async function handleCreate(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setSubmitting(true)
    try {
      await createBlacklistEntry({ ...form, created_by: 'frontend' })
      await blacklistState.reload()
    } finally {
      setSubmitting(false)
    }
  }

  async function handleDelete(id: number) {
    await deleteBlacklistEntry(id)
    await blacklistState.reload()
  }

  return (
    <section className="content-stack">
      <section className="card">
        <p className="eyebrow">黑名单</p>
        <h2>恶意来源管理</h2>
        <p className="subtitle">
          查看自动拉黑记录，手动添加可疑来源，也可以移除临时封禁。
        </p>

        <form className="form-grid compact-top" onSubmit={handleCreate}>
          <label>
            来源 IP
            <input
              value={form.source_ip}
              onChange={(event) => setForm((current) => ({ ...current, source_ip: event.target.value }))}
            />
          </label>
          <label>
            来源端口
            <input
              type="number"
              value={form.source_port}
              onChange={(event) => setForm((current) => ({ ...current, source_port: Number(event.target.value) }))}
            />
          </label>
          <label>
            攻击类型
            <select
              value={form.attack_type}
              onChange={(event) => setForm((current) => ({ ...current, attack_type: event.target.value }))}
            >
              <option value="arp_spoof">{formatTrafficLabel('arp_spoof')}</option>
              <option value="ddos">{formatTrafficLabel('ddos')}</option>
              <option value="trojan">{formatTrafficLabel('trojan')}</option>
            </select>
          </label>
          <label>
            风险等级
            <select
              value={form.risk_level}
              onChange={(event) => setForm((current) => ({ ...current, risk_level: event.target.value }))}
            >
              <option value="low">{formatRiskLevel('low')}</option>
              <option value="medium">{formatRiskLevel('medium')}</option>
              <option value="high">{formatRiskLevel('high')}</option>
            </select>
          </label>
          <label className="span-2">
            原因
            <input
              value={form.reason}
              onChange={(event) => setForm((current) => ({ ...current, reason: event.target.value }))}
            />
          </label>
          <button className="primary-button" type="submit" disabled={submitting}>
            {submitting ? '正在提交...' : '添加黑名单记录'}
          </button>
        </form>
      </section>

      <DataState
        loading={blacklistState.loading}
        error={blacklistState.error}
        empty={!blacklistState.data?.length}
        emptyMessage="黑名单为空。"
      >
        <PanelTable
          title="黑名单记录"
          columns={[
            { key: 'source_ip', title: '来源 IP', render: (row) => row.source_ip },
            { key: 'attack_type', title: '攻击类型', render: (row) => formatTrafficLabel(row.attack_type) },
            {
              key: 'risk_level',
              title: '风险等级',
              render: (row) => <Badge tone={toBadgeTone(row.risk_level)}>{formatRiskLevel(row.risk_level)}</Badge>,
            },
            { key: 'hit_count', title: '命中次数', render: (row) => row.hit_count },
            { key: 'status', title: '状态', render: (row) => formatStatus(row.status) },
            { key: 'reason', title: '原因', render: (row) => formatReason(row.reason) },
            { key: 'last_seen_at', title: '最近出现', render: (row) => formatTimestamp(row.last_seen_at) },
            {
              key: 'actions',
              title: '操作',
              render: (row) => (
                <button className="inline-button" type="button" onClick={() => void handleDelete(row.id)}>
                  移除
                </button>
              ),
            },
          ]}
          rows={blacklistState.data ?? []}
        />
      </DataState>
    </section>
  )
}

export default BlacklistPage
