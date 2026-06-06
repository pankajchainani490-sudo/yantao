import { useEffect, useState } from 'react'

type AsyncState<T> = {
  data: T | null
  loading: boolean
  error: string | null
  reload: () => Promise<void>
}

export function useAsyncData<T>(loader: () => Promise<T>, deps: unknown[] = []): AsyncState<T> {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  async function run() {
    setLoading(true)
    setError(null)

    try {
      const result = await loader()
      setData(result)
    } catch (caughtError) {
      const message = caughtError instanceof Error ? caughtError.message : '未知请求错误'
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void run()
  }, deps)

  return {
    data,
    loading,
    error,
    reload: run,
  }
}
