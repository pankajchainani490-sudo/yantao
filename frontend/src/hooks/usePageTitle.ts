import { useEffect } from 'react'

export function usePageTitle(title: string) {
  useEffect(() => {
    document.title = `${title} | 恶意流量识别控制台`
  }, [title])
}
