import type { ReactElement } from 'react'

import DashboardPage from '../pages/DashboardPage'
import DetectionPage from '../pages/DetectionPage'
import ReplayPage from '../pages/ReplayPage'
import BlacklistPage from '../pages/BlacklistPage'
import ModelMetricsPage from '../pages/ModelMetricsPage'
import SettingsPage from '../pages/SettingsPage'

export type AppRoute = {
  path: string
  navPath: string
  label: string
  element: ReactElement
  index?: boolean
}

export const consoleRoutes: AppRoute[] = [
  { path: '', navPath: '/console', label: '总览看板', element: <DashboardPage />, index: true },
  { path: 'detection', navPath: '/console/detection', label: '流量检测', element: <DetectionPage /> },
  { path: 'replay', navPath: '/console/replay', label: '演示回放', element: <ReplayPage /> },
  { path: 'blacklist', navPath: '/console/blacklist', label: '黑名单', element: <BlacklistPage /> },
  { path: 'metrics', navPath: '/console/metrics', label: '模型指标', element: <ModelMetricsPage /> },
  { path: 'settings', navPath: '/console/settings', label: '系统设置', element: <SettingsPage /> },
]
