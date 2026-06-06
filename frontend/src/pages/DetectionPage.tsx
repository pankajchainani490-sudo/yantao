import { useState } from 'react'

import Badge from '../components/Badge'
import DataState from '../components/DataState'
import { getSettings, predict, type PredictionRequest } from '../api/security'
import { useAsyncData } from '../hooks/useAsyncData'
import { usePageTitle } from '../hooks/usePageTitle'
import { formatPercent } from '../utils/format'
import {
  formatBlacklistAction,
  formatFeatureName,
  formatModelName,
  formatRiskLevel,
  formatTrafficLabel,
} from '../utils/i18n'

function DetectionPage() {
  usePageTitle('流量检测')
  const settingsState = useAsyncData(getSettings, [])
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<Awaited<ReturnType<typeof predict>> | null>(null)
  const [form, setForm] = useState<PredictionRequest>({
    source_ip: '10.10.0.200',
    destination_ip: '172.16.0.99',
    source_port: 43111,
    destination_port: 80,
    packet_len_mean: 132.6,
    packet_len_max: 526.0,
    packet_len_min: 60.0,
    packet_len_std: 45.0,
    packets_per_sec: 1490.4,
    bytes_per_sec: 194880.0,
    flow_duration: 3.1,
    model_name: 'random_forest',
  })

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setSubmitting(true)
    setError(null)

    try {
      const response = await predict(form)
      setResult(response)
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : '预测失败')
    } finally {
      setSubmitting(false)
    }
  }

  function updateField<K extends keyof PredictionRequest>(key: K, value: PredictionRequest[K]) {
    setForm((current) => ({ ...current, [key]: value }))
  }

  return (
    <section className="content-stack">
      <section className="card">
        <p className="eyebrow">流量检测</p>
        <h2>识别流程</h2>
        <ol className="timeline-list">
          <li>采集或导入流量数据。</li>
          <li>把数据包整理为流记录或时间窗口。</li>
          <li>提取包长、端口、发送频率等特征。</li>
          <li>调用决策树或随机森林模型进行推理。</li>
          <li>输出风险等级、告警事件和黑名单候选结果。</li>
        </ol>
      </section>

      <DataState loading={settingsState.loading} error={settingsState.error}>
        <section className="card">
          <div className="panel-heading">
            <h3>交互式预测</h3>
            <p className="subtitle">提交一个流量窗口，查看模型返回的识别结果。</p>
          </div>

          <form className="form-grid" onSubmit={handleSubmit}>
            <label>
              来源 IP
              <input value={form.source_ip} onChange={(event) => updateField('source_ip', event.target.value)} />
            </label>
            <label>
              目的 IP
              <input
                value={form.destination_ip}
                onChange={(event) => updateField('destination_ip', event.target.value)}
              />
            </label>
            <label>
              来源端口
              <input
                type="number"
                value={form.source_port}
                onChange={(event) => updateField('source_port', Number(event.target.value))}
              />
            </label>
            <label>
              目的端口
              <input
                type="number"
                value={form.destination_port}
                onChange={(event) => updateField('destination_port', Number(event.target.value))}
              />
            </label>
            <label>
              平均包长
              <input
                type="number"
                step="0.1"
                value={form.packet_len_mean}
                onChange={(event) => updateField('packet_len_mean', Number(event.target.value))}
              />
            </label>
            <label>
              最大包长
              <input
                type="number"
                step="0.1"
                value={form.packet_len_max}
                onChange={(event) => updateField('packet_len_max', Number(event.target.value))}
              />
            </label>
            <label>
              最小包长
              <input
                type="number"
                step="0.1"
                value={form.packet_len_min}
                onChange={(event) => updateField('packet_len_min', Number(event.target.value))}
              />
            </label>
            <label>
              包长标准差
              <input
                type="number"
                step="0.1"
                value={form.packet_len_std}
                onChange={(event) => updateField('packet_len_std', Number(event.target.value))}
              />
            </label>
            <label>
              每秒包数
              <input
                type="number"
                step="0.1"
                value={form.packets_per_sec}
                onChange={(event) => updateField('packets_per_sec', Number(event.target.value))}
              />
            </label>
            <label>
              每秒字节数
              <input
                type="number"
                step="0.1"
                value={form.bytes_per_sec}
                onChange={(event) => updateField('bytes_per_sec', Number(event.target.value))}
              />
            </label>
            <label>
              流持续时间
              <input
                type="number"
                step="0.1"
                value={form.flow_duration}
                onChange={(event) => updateField('flow_duration', Number(event.target.value))}
              />
            </label>
            <label>
              模型
              <select
                value={form.model_name}
                onChange={(event) => updateField('model_name', event.target.value)}
              >
                {settingsState.data?.supported_models.map((model) => (
                  <option key={model} value={model}>
                    {formatModelName(model)}
                  </option>
                ))}
              </select>
            </label>
            <button className="primary-button" type="submit" disabled={submitting}>
              {submitting ? '正在预测...' : '开始预测'}
            </button>
          </form>

          {error ? <p className="inline-error">{error}</p> : null}
        </section>
      </DataState>

      {result ? (
        <section className="card">
          <div className="panel-heading">
            <h3>预测结果</h3>
            <Badge tone={result.risk_level as 'low' | 'medium' | 'high'}>{formatRiskLevel(result.risk_level)}</Badge>
          </div>
          <div className="key-value-grid">
            <div>
              <span>分类</span>
              <strong>{formatTrafficLabel(result.predicted_label)}</strong>
            </div>
            <div>
              <span>置信度</span>
              <strong>{formatPercent(result.confidence * 100)}</strong>
            </div>
            <div>
              <span>模型</span>
              <strong>{formatModelName(result.model_name)}</strong>
            </div>
            <div>
              <span>黑名单动作</span>
              <strong>{formatBlacklistAction(result.blacklist_action)}</strong>
            </div>
          </div>

          <div className="content-grid two-up compact-top">
            <section className="card inset-card">
              <h4>关键特征</h4>
              <ul className="feature-list">
                {result.top_features.map((item) => (
                  <li key={item.feature}>
                    <span>{formatFeatureName(item.feature)}</span>
                    <strong>{formatPercent(item.importance * 100)}</strong>
                  </li>
                ))}
              </ul>
            </section>

            <section className="card inset-card">
              <h4>处置结果</h4>
              <ul className="timeline-list compact-list">
                <li>预测编号：{result.prediction_id}</li>
                <li>是否生成告警：{result.alert_created ? '是' : '否'}</li>
                <li>风险等级：{formatRiskLevel(result.risk_level)}</li>
                <li>结果已写入看板，可继续触发黑名单联动。</li>
              </ul>
            </section>
          </div>
        </section>
      ) : null}
    </section>
  )
}

export default DetectionPage
