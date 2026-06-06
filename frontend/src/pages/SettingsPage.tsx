import DataState from '../components/DataState'
import { getSettings } from '../api/security'
import { useAsyncData } from '../hooks/useAsyncData'
import { usePageTitle } from '../hooks/usePageTitle'
import { formatModelName } from '../utils/i18n'

function SettingsPage() {
  usePageTitle('系统设置')
  const settingsState = useAsyncData(getSettings, [])

  return (
    <DataState loading={settingsState.loading} error={settingsState.error}>
      <section className="card">
        <p className="eyebrow">系统设置</p>
        <h2>系统控制面板</h2>
        <div className="key-value-grid compact-top">
          <div>
            <span>默认模型</span>
            <strong>{formatModelName(settingsState.data?.default_model_name)}</strong>
          </div>
          <div>
            <span>支持模型</span>
            <strong>{settingsState.data?.supported_models.map(formatModelName).join('、')}</strong>
          </div>
          <div>
            <span>自动拉黑阈值</span>
            <strong>{settingsState.data?.auto_blacklist_threshold}</strong>
          </div>
          <div>
            <span>演示模式</span>
            <strong>{settingsState.data?.demo_mode ? '已启用' : '已关闭'}</strong>
          </div>
        </div>
      </section>
    </DataState>
  )
}

export default SettingsPage
