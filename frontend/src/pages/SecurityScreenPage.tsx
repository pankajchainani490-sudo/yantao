import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import {
  addLocalhostTarget,
  getDashboardSummary,
  getMonitorEvents,
  getMonitorSummary,
  getMonitorTargets,
  getMetricsSummary,
  getReplayStatus,
  getSimulationScenarios,
  runSimulation,
  type MonitorEvent,
  type SiteTarget,
} from '../api/security'
import { useAsyncData } from '../hooks/useAsyncData'
import { usePageTitle } from '../hooks/usePageTitle'
import { formatPercent } from '../utils/format'
import {
  formatFeatureName,
  formatModelName,
  formatReplayName,
  formatRiskLevel,
  formatTrafficLabel,
} from '../utils/i18n'
import { formatTimestamp } from '../utils/time'

async function loadScreenData(targetId: number | null) {
  const [summary, metrics, replay, targets, monitorSummary, scenarios] = await Promise.all([
    getDashboardSummary(),
    getMetricsSummary(),
    getReplayStatus(),
    getMonitorTargets(),
    getMonitorSummary(targetId),
    getSimulationScenarios(),
  ])
  const monitorEvents = await getMonitorEvents(8, monitorSummary.target.id)

  return { summary, metrics, replay, targets, target: monitorSummary.target, monitorSummary, monitorEvents, scenarios }
}

function formatNumber(value: number) {
  return new Intl.NumberFormat('zh-CN').format(value)
}

function getRiskTone(riskLevel: string) {
  if (riskLevel === 'high') {
    return 'danger'
  }

  if (riskLevel === 'medium') {
    return 'warn'
  }

  return 'safe'
}

function formatTargetLabel(target?: SiteTarget | null) {
  if (!target) {
    return '-'
  }

  return target.display_name || `${target.target_host}:${target.port}`
}

function StatNode({ label, value, meta, tone = 'cyan' }: { label: string; value: string; meta: string; tone?: string }) {
  return (
    <article className={`screen-stat screen-stat-${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{meta}</small>
    </article>
  )
}

function EventRow({ event }: { event: MonitorEvent }) {
  return (
    <li className={`screen-alert-row screen-alert-${getRiskTone(event.risk_level)}`}>
      <span>{formatTrafficLabel(event.predicted_label)}</span>
      <strong>{event.source_ip}</strong>
      <em>{formatRiskLevel(event.risk_level)}</em>
      <small>{formatPercent(event.confidence * 100)}</small>
    </li>
  )
}

function SecurityScreenPage() {
  usePageTitle('安全态势大屏')
  const [selectedTargetId, setSelectedTargetId] = useState<number | null>(null)
  const screenState = useAsyncData(() => loadScreenData(selectedTargetId), [selectedTargetId])
  const [portInput, setPortInput] = useState('3000')
  const [workingAction, setWorkingAction] = useState<string | null>(null)
  const [actionMessage, setActionMessage] = useState<string | null>(null)
  const data = screenState.data
  const monitorSummary = data?.monitorSummary
  const target = data?.target
  const targets = data?.targets ?? []
  const totalPredictions = monitorSummary?.total_events ?? 0
  const maliciousPredictions = monitorSummary?.malicious_events ?? 0
  const benignPredictions = monitorSummary?.benign_events ?? 0
  const maliciousRatio = totalPredictions ? (maliciousPredictions / totalPredictions) * 100 : 0
  const attackLabels = ['arp_spoof', 'ddos', 'trojan']
  const attackStats = attackLabels.map((label) => ({
    label,
    count: monitorSummary?.attack_counts.find((item) => item.label === label)?.count ?? 0,
  }))
  const maxAttackCount = Math.max(...attackStats.map((item) => item.count), 1)
  const latestEvents = data?.monitorEvents ?? []
  const randomForestFeatures = data?.metrics.feature_importance.random_forest.slice(0, 6) ?? []
  const currentTime = new Date().toLocaleString('zh-CN', { hour12: false })

  useEffect(() => {
    if (target && selectedTargetId === null) {
      setSelectedTargetId(target.id)
    }
  }, [selectedTargetId, target?.id])

  async function handleAddLocalPort(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setWorkingAction('target')
    setActionMessage(null)
    try {
      const port = Number(portInput)
      if (!Number.isInteger(port) || port < 1 || port > 65535) {
        throw new Error('请输入 1 到 65535 之间的 localhost 端口。')
      }

      const createdTarget = await addLocalhostTarget({
        port,
        scheme: 'http',
        display_name: `localhost:${port}`,
      })
      setSelectedTargetId(createdTarget.id)
      if (selectedTargetId === createdTarget.id) {
        await screenState.reload()
      }
      setActionMessage(`已切换到 ${formatTargetLabel(createdTarget)}，该识别对象拥有独立统计。`)
    } catch (error) {
      setActionMessage(error instanceof Error ? error.message : 'localhost 端口添加失败')
    } finally {
      setWorkingAction(null)
    }
  }

  async function handleSimulation(scenario: string) {
    setWorkingAction(scenario)
    setActionMessage(null)
    try {
      const response = await runSimulation({
        scenario,
        count: scenario === 'normal_visit' ? 3 : 5,
        target_id: target?.id,
      })
      await screenState.reload()
      setActionMessage(`已为 ${formatTargetLabel(target)} 生成 ${response.count} 条模拟观测事件，模型已完成识别。`)
    } catch (error) {
      setActionMessage(error instanceof Error ? error.message : '模拟攻击失败')
    } finally {
      setWorkingAction(null)
    }
  }

  if (screenState.loading) {
    return (
      <main className="screen-shell screen-loading">
        <div className="screen-loading-core">安全态势数据加载中...</div>
      </main>
    )
  }

  if (screenState.error) {
    return (
      <main className="screen-shell screen-loading">
        <div className="screen-loading-core screen-loading-error">{screenState.error}</div>
      </main>
    )
  }

  return (
    <main className="screen-shell">
      <header className="screen-topbar">
        <div>
          <p>恶意流量识别系统</p>
          <h1>安全态势感知大屏</h1>
        </div>
        <div className="screen-top-actions">
          <span>系统时间 {currentTime}</span>
          <Link className="screen-console-link" to="/console">
            进入后台 <span aria-hidden="true">›</span>
          </Link>
        </div>
      </header>

      <section className="screen-control-panel">
        <form className="screen-target-form" onSubmit={handleAddLocalPort}>
          <label className="screen-target-picker">
            已添加识别对象
            <select
              value={selectedTargetId ?? target?.id ?? ''}
              onChange={(event) => {
                setActionMessage(null)
                setSelectedTargetId(Number(event.target.value))
              }}
            >
              {targets.map((item) => (
                <option value={item.id} key={item.id}>
                  {formatTargetLabel(item)}
                </option>
              ))}
            </select>
          </label>
          <label>
            新增 localhost 端口
            <input
              type="number"
              min="1"
              max="65535"
              value={portInput}
              placeholder="例如 3000"
              onChange={(event) => setPortInput(event.target.value)}
            />
          </label>
          <button type="submit" disabled={workingAction === 'target'}>
            {workingAction === 'target' ? '添加中...' : '添加对象'}
          </button>
        </form>

        <div className="screen-sim-actions">
          {(data?.scenarios ?? [])
            .filter((scenario) => scenario.id !== 'arp_spoof_lab')
            .map((scenario) => (
              <button
                type="button"
                key={scenario.id}
                disabled={Boolean(workingAction)}
                onClick={() => void handleSimulation(scenario.id)}
              >
                {workingAction === scenario.id ? '模拟中...' : `模拟${scenario.title}`}
              </button>
            ))}
        </div>
        <div className="screen-target-status">
          <span>当前识别对象：{formatTargetLabel(target)} · {target?.target_url ?? '-'}</span>
          <small>{actionMessage ?? '新增端口会从 0 开始统计；模拟按钮只生成受控观测事件。'}</small>
        </div>
      </section>

      <section className="screen-layout">
        <aside className="screen-column">
          <section className="screen-panel screen-panel-primary">
            <div className="screen-panel-title">
              <span>总体态势</span>
              <strong>实时统计</strong>
            </div>
            <div className="screen-stat-grid">
              <StatNode label="识别总量" value={formatNumber(totalPredictions)} meta="当前对象推理记录" />
              <StatNode label="恶意识别" value={formatNumber(maliciousPredictions)} meta="当前对象非正常流量" tone="red" />
              <StatNode label="正常流量" value={formatNumber(benignPredictions)} meta="当前对象低风险基线" tone="green" />
              <StatNode
                label="黑名单"
                value={formatNumber(data?.summary.blacklist_count ?? 0)}
                meta="全局封禁来源"
                tone="amber"
              />
            </div>
          </section>

          <section className="screen-panel">
            <div className="screen-panel-title">
              <span>攻击类型</span>
              <strong>分布</strong>
            </div>
            <div className="screen-bars">
              {attackStats.map((item) => (
                <div className="screen-bar-row" key={item.label}>
                  <div>
                    <span>{formatTrafficLabel(item.label)}</span>
                    <strong>{item.count}</strong>
                  </div>
                  <div className="screen-bar-track">
                    <i style={{ width: `${(item.count / maxAttackCount) * 100}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </section>

          <section className="screen-panel">
            <div className="screen-panel-title">
              <span>高频来源</span>
              <strong>前 {monitorSummary?.top_sources.length ?? 0}</strong>
            </div>
            <ul className="screen-source-list">
              {monitorSummary?.top_sources.map((source) => (
                <li key={`${source.source_ip}-${source.attack_type}`}>
                  <span>{source.source_ip}</span>
                  <strong>{formatTrafficLabel(source.attack_type)}</strong>
                  <small>{source.hit_count} 次 / {formatPercent(source.max_confidence * 100)}</small>
                </li>
              ))}
            </ul>
          </section>
        </aside>

        <section className="screen-center">
          <div className="screen-radar">
            <div className="screen-radar-ring screen-radar-ring-outer" />
            <div className="screen-radar-ring screen-radar-ring-mid" />
            <div className="screen-radar-core">
              <span>恶意占比</span>
              <strong>{formatPercent(maliciousRatio)}</strong>
              <small>{monitorSummary?.open_alerts ?? 0} 条待处理告警</small>
            </div>
            <div className="screen-radar-sweep" />
            <div className="screen-pulse screen-pulse-a" />
            <div className="screen-pulse screen-pulse-b" />
            <div className="screen-pulse screen-pulse-c" />
          </div>

          <div className="screen-flow-board">
            <div>
              <span>入口流量</span>
              <strong>{formatNumber(totalPredictions)}</strong>
            </div>
            <i />
            <div>
              <span>模型判定</span>
              <strong>{formatModelName(data?.metrics.models.random_forest ? 'random_forest' : 'decision_tree')}</strong>
            </div>
            <i />
            <div>
              <span>联动处置</span>
              <strong>{data?.summary.replay_running ? '回放运行中' : '待命监测'}</strong>
            </div>
          </div>

          <section className="screen-panel screen-wide-panel">
            <div className="screen-panel-title">
              <span>模型能力</span>
              <strong>准确率 / 召回率 / F1</strong>
            </div>
            <div className="screen-model-grid">
              {Object.entries(data?.metrics.models ?? {}).map(([modelName, metrics]) => (
                <article key={modelName}>
                  <span>{formatModelName(modelName)}</span>
                  <strong>{formatPercent(metrics.accuracy * 100)}</strong>
                  <small>
                    召回 {formatPercent(metrics.recall_macro * 100)} · F1 {formatPercent(metrics.f1_macro * 100)}
                  </small>
                </article>
              ))}
            </div>
          </section>
        </section>

        <aside className="screen-column">
          <section className="screen-panel screen-alert-panel">
            <div className="screen-panel-title">
              <span>最新告警</span>
              <strong>{latestEvents.length} 条</strong>
            </div>
            <ul className="screen-alert-list">
              {latestEvents.map((event) => (
                <EventRow event={event} key={event.id} />
              ))}
              {!latestEvents.length ? <li className="screen-empty-row">暂无实时观测事件，点击上方模拟按钮开始验证。</li> : null}
            </ul>
          </section>

          <section className="screen-panel">
            <div className="screen-panel-title">
              <span>关键特征</span>
              <strong>随机森林</strong>
            </div>
            <div className="screen-feature-stack">
              {randomForestFeatures.map((feature) => (
                <div key={feature.feature}>
                  <span>{formatFeatureName(feature.feature)}</span>
                  <strong>{formatPercent(feature.importance * 100)}</strong>
                </div>
              ))}
            </div>
          </section>

          <section className="screen-panel">
            <div className="screen-panel-title">
              <span>回放状态</span>
              <strong>{formatReplayName(data?.replay.name)}</strong>
            </div>
            <div className="screen-replay-card">
              <div>
                <span>当前阶段</span>
                <strong>{data?.replay.current_stage ?? 0}</strong>
              </div>
              <div>
                <span>当前分类</span>
                <strong>{formatTrafficLabel(data?.replay.current_label)}</strong>
              </div>
              <div>
                <span>更新时间</span>
                <strong>{data?.replay.updated_at ? formatTimestamp(data.replay.updated_at) : '-'}</strong>
              </div>
            </div>
          </section>
        </aside>
      </section>
    </main>
  )
}

export default SecurityScreenPage
