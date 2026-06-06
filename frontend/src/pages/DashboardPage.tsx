import DataState from '../components/DataState'
import PanelTable from '../components/PanelTable'
import StatCard from '../components/StatCard'
import { getAlerts, getDashboardSummary, getDashboardTrends, getTopSources } from '../api/security'
import { useAsyncData } from '../hooks/useAsyncData'
import { usePageTitle } from '../hooks/usePageTitle'
import { formatPercent } from '../utils/format'
import { formatRiskLevel, formatTrafficLabel } from '../utils/i18n'
import { formatTimestamp } from '../utils/time'

function DashboardPage() {
  usePageTitle('总览看板')
  const summaryState = useAsyncData(getDashboardSummary, [])
  const trendsState = useAsyncData(getDashboardTrends, [])
  const topSourcesState = useAsyncData(getTopSources, [])
  const alertsState = useAsyncData(() => getAlerts(6), [])

  const summary = summaryState.data
  const total = summary?.total_predictions ?? 0
  const maliciousRatio = total ? ((summary?.malicious_predictions ?? 0) / total) * 100 : 0

  const stats = [
    {
      title: '识别记录总数',
      value: String(summary?.total_predictions ?? 0),
      hint: 'SQLite 中已保存的正常与恶意推理记录',
    },
    {
      title: '恶意占比',
      value: formatPercent(maliciousRatio),
      hint: 'ARP 欺骗、DDoS 洪泛和木马通信的分类占比',
    },
    {
      title: '待处理告警',
      value: String(summary?.open_alerts ?? 0),
      hint: '等待人工复核或自动处置的事件',
    },
    {
      title: '黑名单数量',
      value: String(summary?.blacklist_count ?? 0),
      hint: summary?.replay_running ? '演示回放正在运行' : '演示回放当前空闲',
    },
  ]

  return (
    <section>
      <header className="page-header">
        <div>
          <p className="eyebrow">总览看板</p>
          <h2>流量安全态势</h2>
          <p className="subtitle">
            基于后端接口展示识别总量、恶意占比、最新告警和高频恶意来源。
          </p>
        </div>
      </header>

      <DataState loading={summaryState.loading} error={summaryState.error}>
        <div className="stats-grid">
          {stats.map((stat) => (
            <StatCard key={stat.title} title={stat.title} value={stat.value} hint={stat.hint} />
          ))}
        </div>
      </DataState>

      <div className="content-grid two-up">
        <DataState
          loading={trendsState.loading}
          error={trendsState.error}
          empty={!trendsState.data?.length}
          emptyMessage="暂无趋势数据。"
        >
          <PanelTable
            title="趋势统计"
            columns={[
              { key: 'bucket', title: '时间段', render: (row) => row.bucket },
              { key: 'label', title: '分类', render: (row) => formatTrafficLabel(row.label) },
              { key: 'count', title: '数量', render: (row) => row.count },
            ]}
            rows={trendsState.data ?? []}
          />
        </DataState>

        <DataState
          loading={topSourcesState.loading}
          error={topSourcesState.error}
          empty={!topSourcesState.data?.length}
          emptyMessage="暂无恶意来源记录。"
        >
          <PanelTable
            title="高频恶意来源"
            columns={[
              { key: 'source_ip', title: '来源 IP', render: (row) => row.source_ip },
              { key: 'attack_type', title: '攻击类型', render: (row) => formatTrafficLabel(row.attack_type) },
              { key: 'hit_count', title: '命中次数', render: (row) => row.hit_count },
              {
                key: 'max_confidence',
                title: '最高置信度',
                render: (row) => formatPercent(row.max_confidence * 100),
              },
            ]}
            rows={topSourcesState.data ?? []}
          />
        </DataState>
      </div>

      <DataState
        loading={alertsState.loading}
        error={alertsState.error}
        empty={!alertsState.data?.length}
        emptyMessage="暂无告警记录。"
      >
        <PanelTable
          title="最新告警"
          columns={[
            { key: 'source_ip', title: '来源', render: (row) => row.source_ip },
            { key: 'attack_type', title: '攻击类型', render: (row) => formatTrafficLabel(row.attack_type) },
            { key: 'risk_level', title: '风险等级', render: (row) => formatRiskLevel(row.risk_level) },
            {
              key: 'confidence',
              title: '置信度',
              render: (row) => formatPercent(row.confidence * 100),
            },
            { key: 'created_at', title: '生成时间', render: (row) => formatTimestamp(row.created_at) },
          ]}
          rows={alertsState.data ?? []}
        />
      </DataState>
    </section>
  )
}

export default DashboardPage
