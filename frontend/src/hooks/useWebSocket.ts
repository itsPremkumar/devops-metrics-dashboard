import { useEffect, useRef } from 'react'

export function useWebSocket(
  url: string,
  onMessage: (data: any) => void,
  onConnected?: (isConnected: boolean) => void
) {
  const ws = useRef<WebSocket | null>(null)

  useEffect(() => {
    const connect = () => {
      ws.current = new WebSocket(url)

      ws.current.onopen = () => {
        onConnected?.(true)
        console.log('WebSocket connected')
      }

      ws.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          onMessage(data)
        } catch (e) {
          console.error('WebSocket message parse error:', e)
        }
      }

      ws.current.onclose = () => {
        onConnected?.(false)
        console.log('WebSocket disconnected — reconnecting in 5s')
        setTimeout(connect, 5000)
      }

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error)
        ws.current?.close()
      }
    }

    connect()

    return () => {
      ws.current?.close()
    }
  }, [url])
}
