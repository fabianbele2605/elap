import { useState, useEffect, useCallback, useRef } from 'react'

export default function useWebSocketStream(agentId, query) {
  const [isStreaming, setIsStreaming] = useState(false)
  const [messages, setMessages] = useState([])
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState(null)
  const wsRef = useRef(null)
  const messagesRef = useRef([])

  const startStream = useCallback(() => {
    if (!agentId || !query) {
      setError('Agent ID and query required')
      return
    }

    setIsStreaming(true)
    setProgress(0)
    setError(null)
    messagesRef.current = []

    try {
      const wsUrl = `ws://localhost:3000/agents/${agentId}/execute/stream`
      const ws = new WebSocket(wsUrl)

      ws.onopen = () => {
        console.log('✅ WebSocket conectado')
        setIsStreaming(true)
        // Enviar query
        ws.send(JSON.stringify({ query }))
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)

          switch (data.tipo) {
            case 'iniciado':
              setProgress(5)
              break

            case 'procesando':
              setProgress(15)
              break

            case 'token':
              // Acumular token
              const newText = messagesRef.current.join('') + data.chunk
              messagesRef.current.push(data.chunk)
              setMessages([...messagesRef.current])
              setProgress(Math.min(data.progress || 50, 95))
              break

            case 'progreso':
              setProgress(data.progress || 50)
              break

            case 'completado':
              setProgress(100)
              setIsStreaming(false)
              break

            case 'error':
              setError(data.mensaje || 'Error en streaming')
              setIsStreaming(false)
              break

            default:
              console.log('Evento:', data.tipo)
          }
        } catch (e) {
          console.error('Error parsing message:', e)
        }
      }

      ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error)
        setError('Error de conexión WebSocket')
        setIsStreaming(false)
      }

      ws.onclose = () => {
        console.log('WebSocket cerrado')
        if (isStreaming) {
          setProgress(100)
          setIsStreaming(false)
        }
      }

      wsRef.current = ws
    } catch (err) {
      console.error('Error al conectar WebSocket:', err)
      setError(err.message)
      setIsStreaming(false)
    }
  }, [agentId, query])

  const stopStream = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
    setIsStreaming(false)
  }, [])

  // Cleanup al desmontar
  useEffect(() => {
    return () => {
      stopStream()
    }
  }, [stopStream])

  return {
    isStreaming,
    messages,
    text: messages.join(''),
    progress,
    error,
    startStream,
    stopStream
  }
}
