import DataState from '../components/DataState'
import Badge from '../components/Badge'
import { getReplayStatus, startReplay } from '../api/security'
import { useAsyncData } from '../hooks/useAsyncData'
import { usePageTitle } from '../hooks/usePageTitle'
import { formatReplayName, formatReplayPurpose, formatTrafficLabel } from '../utils/i18n'
import { formatTimestamp } from '../utils/time'

function ReplayPage() {
  usePageTitle('演示回放')
  const replayState = useAsyncData(getReplayStatus, [])

  async function handleStageStart(stageOrder: number) {
    await startReplay(stageOrder)
    await replayState.reload()
  }

  return (
    <DataState loading={replayState.loading} error={replayState.error}>
      <section className="content-stack">
        <section className="card">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">演示回放</p>
              <h2>流量回放工作台</h2>
              <p className="subtitle">
                按阶段从正常流量切换到不同攻击场景，便于稳定演示识别效果。
              </p>
            </div>
            <Badge tone={replayState.data?.is_running ? 'active' : 'neutral'}>
              {replayState.data?.is_running ? '运行中' : '空闲'}
            </Badge>
          </div>

          <div className="key-value-grid compact-top">
            <div>
              <span>回放名称</span>
              <strong>{formatReplayName(replayState.data?.name)}</strong>
            </div>
            <div>
              <span>当前阶段</span>
              <strong>{replayState.data?.current_stage}</strong>
            </div>
            <div>
              <span>当前分类</span>
              <strong>{formatTrafficLabel(replayState.data?.current_label)}</strong>
            </div>
            <div>
              <span>更新时间</span>
              <strong>{replayState.data ? formatTimestamp(replayState.data.updated_at) : '-'}</strong>
            </div>
          </div>

          <div className="progress-bar compact-top">
            <div
              className="progress-value"
              style={{ width: `${(replayState.data?.progress ?? 0) * 100}%` }}
            />
          </div>
        </section>

        <section className="card">
          <div className="panel-heading">
            <h3>回放阶段</h3>
          </div>
          <div className="stage-grid">
            {replayState.data?.stages.map((stage) => (
              <article key={stage.order} className="card inset-card stage-card">
                <p className="eyebrow">阶段 {stage.order}</p>
                <h4>{formatTrafficLabel(stage.label)}</h4>
                <p className="subtitle">{formatReplayPurpose(stage.label, stage.purpose)}</p>
                <p className="subtitle">数据文件：{stage.source}</p>
                <button className="primary-button" type="button" onClick={() => void handleStageStart(stage.order)}>
                  启动阶段
                </button>
              </article>
            ))}
          </div>
        </section>
      </section>
    </DataState>
  )
}

export default ReplayPage
