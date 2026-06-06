export const apiBaseUrl = '/api/v1'

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
    ...init,
  })

  if (!response.ok) {
    const body = await response.json().catch(() => null)
    const detail = body && typeof body === 'object' && 'detail' in body ? String(body.detail) : response.statusText
    throw new Error(detail || `请求失败：${response.status}`)
  }

  return (await response.json()) as T
}
