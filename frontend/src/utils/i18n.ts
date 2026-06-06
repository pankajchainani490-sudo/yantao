const trafficLabelMap: Record<string, string> = {
  benign: '正常流量',
  arp_spoof: 'ARP 欺骗',
  ddos: 'DDoS 洪泛',
  trojan: '木马通信',
}

const riskLevelMap: Record<string, string> = {
  low: '低风险',
  medium: '中风险',
  high: '高风险',
}

const modelNameMap: Record<string, string> = {
  decision_tree: '决策树',
  random_forest: '随机森林',
}

const featureNameMap: Record<string, string> = {
  src_port: '源端口',
  dst_port: '目的端口',
  packet_len_mean: '平均包长',
  packet_len_max: '最大包长',
  packet_len_min: '最小包长',
  packet_len_std: '包长标准差',
  packets_per_sec: '每秒包数',
  bytes_per_sec: '每秒字节数',
  flow_duration: '流持续时间',
  packet_len_range: '包长范围',
  bytes_per_packet: '每包平均字节数',
  port_gap: '端口差值',
  is_system_src_port: '源端口为系统端口',
  is_system_dst_port: '目的端口为系统端口',
  throughput_per_duration: '单位时长吞吐量',
}

const blacklistActionMap: Record<string, string> = {
  none: '未触发拉黑',
  candidate: '已生成候选',
  upserted: '已写入或更新黑名单',
}

const statusMap: Record<string, string> = {
  open: '待处理',
  active: '生效中',
  inactive: '已停用',
  frontend: '前端页面',
  system: '系统自动',
}

const replayPurposeByLabel: Record<string, string> = {
  benign: '建立正常流量基线。',
  arp_spoof: '触发 ARP 欺骗告警，并生成黑名单候选记录。',
  ddos: '展示突发洪泛流量、告警数量上升和看板趋势变化。',
  trojan: '演示疑似命令控制通信的分类结果。',
}

export function formatTrafficLabel(label?: string) {
  return label ? trafficLabelMap[label] ?? label : '-'
}

export function formatRiskLevel(level?: string) {
  return level ? riskLevelMap[level] ?? level : '-'
}

export function formatModelName(modelName?: string) {
  return modelName ? modelNameMap[modelName] ?? modelName : '-'
}

export function formatFeatureName(feature?: string) {
  return feature ? featureNameMap[feature] ?? feature : '-'
}

export function formatBlacklistAction(action?: string) {
  return action ? blacklistActionMap[action] ?? action : '-'
}

export function formatStatus(status?: string) {
  return status ? statusMap[status] ?? status : '-'
}

export function formatReplayName(name?: string) {
  if (!name) {
    return '-'
  }

  if (name === 'demo_replay_baseline') {
    return '演示回放基线'
  }

  return name
}

export function formatReplayPurpose(label?: string, fallback?: string) {
  return label ? replayPurposeByLabel[label] ?? fallback ?? '-' : fallback ?? '-'
}

export function formatReason(reason?: string) {
  if (!reason) {
    return '-'
  }

  const autoBlacklistMatch = reason.match(/^Auto-blacklisted after (\d+) ([a-z_]+) alerts\.$/)
  if (autoBlacklistMatch) {
    return `同一来源累计 ${autoBlacklistMatch[1]} 次 ${formatTrafficLabel(autoBlacklistMatch[2])} 告警后自动拉黑。`
  }

  const knownReasons: Record<string, string> = {
    'Repeated ARP spoof alerts in demo seed data.': '演示种子数据中多次出现 ARP 欺骗告警。',
    'Repeated DDoS alerts in demo seed data.': '演示种子数据中多次出现 DDoS 洪泛告警。',
    'Manual review during frontend integration.': '前端联调期间手动复核。',
  }

  return knownReasons[reason] ?? reason
}
