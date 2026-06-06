import Badge from '../components/Badge'
import DataState from '../components/DataState'
import PanelTable from '../components/PanelTable'
import { getMetricsSummary } from '../api/security'
import { useAsyncData } from '../hooks/useAsyncData'
import { usePageTitle } from '../hooks/usePageTitle'
import { formatPercent } from '../utils/format'
import { formatFeatureName, formatModelName, formatTrafficLabel } from '../utils/i18n'

function ModelMetricsPage() {
  usePageTitle('模型指标')
  const metricsState = useAsyncData(getMetricsSummary, [])

  const randomForestImportance = metricsState.data?.feature_importance.random_forest.slice(0, 8) ?? []
  const decisionTreeImportance = metricsState.data?.feature_importance.decision_tree.slice(0, 8) ?? []

  return (
    <DataState loading={metricsState.loading} error={metricsState.error}>
      <section className="content-stack">
        <section className="card">
          <p className="eyebrow">模型指标</p>
          <h2>模型对比</h2>
          <p className="subtitle">
            对比决策树和随机森林的基础指标、特征重要性和混淆矩阵。
          </p>
          <p className="metric-highlight">恶意流量召回率目标：{formatPercent(90)}</p>
        </section>

        <div className="content-grid two-up">
          {Object.entries(metricsState.data?.models ?? {}).map(([modelName, metrics]) => (
            <section className="card" key={modelName}>
              <div className="panel-heading">
                <h3>{formatModelName(modelName)}</h3>
                <Badge tone="active">已就绪</Badge>
              </div>
              <div className="key-value-grid compact-top">
                <div>
                  <span>准确率</span>
                  <strong>{formatPercent(metrics.accuracy * 100)}</strong>
                </div>
                <div>
                  <span>精确率</span>
                  <strong>{formatPercent(metrics.precision_macro * 100)}</strong>
                </div>
                <div>
                  <span>召回率</span>
                  <strong>{formatPercent(metrics.recall_macro * 100)}</strong>
                </div>
                <div>
                  <span>F1 值</span>
                  <strong>{formatPercent(metrics.f1_macro * 100)}</strong>
                </div>
              </div>
              <p className="subtitle compact-top">
                矩阵顺序：
                {metricsState.data?.confusion_matrices[modelName]?.labels.map(formatTrafficLabel).join('、')}
              </p>
              <div className="matrix-grid compact-top">
                {metrics.confusion_matrix.map((row, rowIndex) => (
                  <div className="matrix-row" key={`${modelName}-${rowIndex}`}>
                    {row.map((value, columnIndex) => (
                      <span className="matrix-cell" key={`${modelName}-${rowIndex}-${columnIndex}`}>
                        {value}
                      </span>
                    ))}
                  </div>
                ))}
              </div>
            </section>
          ))}
        </div>

        <div className="content-grid two-up">
          <PanelTable
            title="随机森林特征重要性"
            columns={[
              { key: 'feature', title: '特征', render: (row) => formatFeatureName(row.feature) },
              {
                key: 'importance',
                title: '重要性',
                render: (row) => formatPercent(row.importance * 100),
              },
            ]}
            rows={randomForestImportance}
          />

          <PanelTable
            title="决策树特征重要性"
            columns={[
              { key: 'feature', title: '特征', render: (row) => formatFeatureName(row.feature) },
              {
                key: 'importance',
                title: '重要性',
                render: (row) => formatPercent(row.importance * 100),
              },
            ]}
            rows={decisionTreeImportance}
          />
        </div>
      </section>
    </DataState>
  )
}

export default ModelMetricsPage
