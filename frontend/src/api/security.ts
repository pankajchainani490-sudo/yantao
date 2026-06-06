import { apiBaseUrl, apiFetch } from './client'

export type DashboardSummary = {
  total_predictions: number
  malicious_predictions: number
  benign_predictions: number
  open_alerts: number
  blacklist_count: number
  replay_running: boolean
}

export type DashboardTrendItem = {
  bucket: string
  label: string
  count: number
}

export type TopSourceItem = {
  source_ip: string
  attack_type: string
  hit_count: number
  max_confidence: number
}

export type AlertItem = {
  id: number
  source_ip: string
  source_port: number
  destination_ip: string
  destination_port: number
  attack_type: string
  risk_level: string
  confidence: number
  status: string
  created_at: string
}

export type BlacklistItem = {
  id: number
  source_ip: string
  source_port: number
  attack_type: string
  risk_level: string
  hit_count: number
  first_seen_at: string
  last_seen_at: string
  status: string
  reason: string
  created_by: string
}

export type FeatureImportanceItem = {
  feature: string
  importance: number
}

export type MetricsSummary = {
  dataset: {
    rows: number
    feature_columns: string[]
    train_rows: number
    test_rows: number
  }
  models: Record<
    string,
    {
      accuracy: number
      precision_macro: number
      recall_macro: number
      f1_macro: number
      confusion_matrix: number[][]
    }
  >
  feature_importance: Record<string, FeatureImportanceItem[]>
  confusion_matrices: Record<
    string,
    {
      labels: string[]
      label_ids: number[]
      matrix: number[][]
    }
  >
}

export type AppSettings = {
  default_model_name: string
  supported_models: string[]
  auto_blacklist_threshold: number
  demo_mode: boolean
}

export type ReplayState = {
  id?: number
  is_running: boolean
  current_stage: number
  current_label: string
  progress: number
  updated_at: string
  name: string
  stages: Array<{
    order: number
    label: string
    source: string
    purpose: string
  }>
}

export type PredictionRequest = {
  source_ip: string
  destination_ip: string
  source_port: number
  destination_port: number
  packet_len_mean: number
  packet_len_max: number
  packet_len_min: number
  packet_len_std: number
  packets_per_sec: number
  bytes_per_sec: number
  flow_duration: number
  model_name?: string
}

export type PredictionResponse = {
  predicted_label: string
  predicted_label_id: number
  confidence: number
  risk_level: string
  model_name: string
  top_features: FeatureImportanceItem[]
  prediction_id: number
  alert_created: boolean
  blacklist_action: string
}

export type BlacklistCreateRequest = {
  source_ip: string
  source_port: number
  attack_type: string
  risk_level: string
  reason: string
  created_by?: string
}

export type SiteTarget = {
  id: number
  target_host: string
  scheme: string
  port: number
  target_url: string
  display_name: string
  is_active: boolean
  updated_at: string
}

export type MonitorEvent = {
  id: number
  target_id: number | null
  target_host: string
  target_url: string
  source_ip: string
  source_port: number
  destination_port: number
  scenario: string
  request_count: number
  packets_per_sec: number
  bytes_per_sec: number
  flow_duration: number
  predicted_label: string
  risk_level: string
  confidence: number
  prediction_id: number
  created_at: string
}

export type MonitorSummary = {
  target: SiteTarget
  total_events: number
  malicious_events: number
  benign_events: number
  open_alerts: number
  latest_event_at: string | null
  attack_counts: Array<{
    label: string
    count: number
  }>
  top_sources: Array<{
    source_ip: string
    attack_type: string
    hit_count: number
    max_confidence: number
  }>
}

export type SiteTargetRequest = {
  target: string
  scheme: string
  port: number
}

export type LocalPortTargetRequest = {
  port: number
  scheme?: string
  display_name?: string
}

export type SimulationScenario = {
  id: string
  label: string
  title: string
  description: string
}

export type SimulationRunRequest = {
  scenario: string
  count?: number
  target_id?: number
  source_ip?: string
  target?: string
  scheme?: string
  port?: number
  model_name?: string
}

export function getDashboardSummary() {
  return apiFetch<DashboardSummary>('/dashboard/summary')
}

export async function getDashboardTrends() {
  const response = await apiFetch<{ items: DashboardTrendItem[] }>('/dashboard/trends')
  return response.items
}

export async function getTopSources() {
  const response = await apiFetch<{ items: TopSourceItem[] }>('/dashboard/top-sources')
  return response.items
}

export async function getAlerts(limit = 50) {
  const response = await apiFetch<{ items: AlertItem[] }>(`/alerts?limit=${limit}`)
  return response.items
}

export async function getBlacklist() {
  const response = await apiFetch<{ items: BlacklistItem[] }>('/blacklist')
  return response.items
}

export async function createBlacklistEntry(payload: BlacklistCreateRequest) {
  const response = await apiFetch<{ item: BlacklistItem }>('/blacklist', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
  return response.item
}

export async function deleteBlacklistEntry(id: number) {
  const response = await fetch(`${apiBaseUrl}/blacklist/${id}`, { method: 'DELETE' })
  if (!response.ok) {
    throw new Error(`删除黑名单记录 ${id} 失败`)
  }
}

export function predict(payload: PredictionRequest) {
  return apiFetch<PredictionResponse>('/predict', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function getMetricsSummary() {
  return apiFetch<MetricsSummary>('/metrics/summary')
}

export function getSettings() {
  return apiFetch<AppSettings>('/settings')
}

export function getReplayStatus() {
  return apiFetch<ReplayState>('/replay/status')
}

export function startReplay(stageOrder: number) {
  return apiFetch<ReplayState>('/replay/start', {
    method: 'POST',
    body: JSON.stringify({ stage_order: stageOrder }),
  })
}

export function getMonitorTarget() {
  return apiFetch<SiteTarget>('/monitor/target')
}

export async function getMonitorTargets() {
  const response = await apiFetch<{ items: SiteTarget[] }>('/monitor/targets')
  return response.items
}

export function setMonitorTarget(payload: SiteTargetRequest) {
  return apiFetch<SiteTarget>('/monitor/target', {
    method: 'PUT',
    body: JSON.stringify(payload),
  })
}

export function addLocalhostTarget(payload: LocalPortTargetRequest) {
  return apiFetch<SiteTarget>('/monitor/targets/localhost', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function getMonitorSummary(targetId?: number | null) {
  const query = targetId ? `?target_id=${targetId}` : ''
  return apiFetch<MonitorSummary>(`/monitor/summary${query}`)
}

export async function getMonitorEvents(limit = 50, targetId?: number | null) {
  const params = new URLSearchParams({ limit: String(limit) })
  if (targetId) {
    params.set('target_id', String(targetId))
  }
  const response = await apiFetch<{ items: MonitorEvent[] }>(`/monitor/events?${params.toString()}`)
  return response.items
}

export async function getSimulationScenarios() {
  const response = await apiFetch<{ items: SimulationScenario[] }>('/simulator/scenarios')
  return response.items
}

export function runSimulation(payload: SimulationRunRequest) {
  return apiFetch<{ scenario: string; expected_label: string; count: number; events: unknown[] }>('/simulator/run', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}
