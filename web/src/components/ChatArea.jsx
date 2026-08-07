import { useState, useRef, useEffect } from 'react'
import useWebSocketStream from '../hooks/useWebSocketStream'
import StreamingMessage from './StreamingMessage'

export default function ChatArea({ agent, messages, activeTab, onTabChange, onMessageSend }) {
  const [inputValue, setInputValue] = useState('')
  const [allMessages, setAllMessages] = useState([])
  const [streamingQuery, setStreamingQuery] = useState(null)
  const { isStreaming, text, progress, error, startStream, stopStream } = useWebSocketStream(agent?.id, streamingQuery)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = () => {
    if (!inputValue.trim() || !agent || isStreaming) return

    const query = inputValue
    const userMessage = {
      id: `msg_${Date.now()}`,
      text: query,
      type: 'user',
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }

    setAllMessages(prev => [...prev, userMessage])
    setInputValue('')

    // Iniciar streaming con WebSocket
    setStreamingQuery(query)
    startStream()
  }

  // Cuando termina el streaming, agregar mensaje a historial
  useEffect(() => {
    if (!isStreaming && text && streamingQuery) {
      const assistantMessage = {
        id: `msg_${Date.now()}_asst`,
        text: text,
        type: 'assistant',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
      setAllMessages(prev => [...prev, assistantMessage])
      setStreamingQuery(null)
    }
  }, [isStreaming, text])

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const tabs = [
    { id: 'chat', label: 'Chat' },
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'tools', label: 'Tools' },
    { id: 'knowledge', label: 'Knowledge' },
    { id: 'history', label: 'History' }
  ]

  return (
    <div className="chat-area">
      {/* Header */}
      <div className="chat-header">
        <div className="chat-header-left">
          {agent && (
            <>
              <div className="agent-badge">
                <div className="badge-dot"></div>
                <span>{agent.name}</span>
              </div>
              <div className="chat-header-divider"></div>
              <span className="model-display">{agent.model}</span>
              <div className="chat-header-divider"></div>
              <div className="status-ready">
                <div className="status-dot"></div>
                <span>Ready</span>
              </div>
            </>
          )}
        </div>
        <div className="chat-header-right">
          <span className="token-counter">Tokens: 523 / 4000</span>
          <div className="chat-header-divider"></div>
          <span className="time-display">
            {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>
      </div>

      {/* Tab Bar */}
      <div className="tab-bar">
        {tabs.map(tab => (
          <div
            key={tab.id}
            className={`tab ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => onTabChange(tab.id)}
          >
            {tab.label}
          </div>
        ))}
      </div>

      {/* Chat Content */}
      {activeTab === 'chat' && (
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
          <div className="chat-messages">
            {allMessages.length === 0 && !isStreaming ? (
              <div style={{ textAlign: 'center', color: '#999999', marginTop: '40px' }}>
                <p style={{ fontSize: '14px' }}>No messages yet</p>
                <p style={{ fontSize: '12px', marginTop: '8px' }}>Start a conversation with the agent</p>
              </div>
            ) : (
              <>
                {allMessages.map(msg => (
                  <div key={msg.id} className={`message ${msg.type}`}>
                    <div>
                      <div className="message-bubble">{msg.text}</div>
                      <span className="message-time">{msg.time}</span>
                    </div>
                  </div>
                ))}

                {/* Mostrar streaming en vivo */}
                {isStreaming && (
                  <StreamingMessage
                    text={text}
                    progress={progress}
                    isStreaming={true}
                    timestamp={new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  />
                )}

                {error && (
                  <div style={{
                    padding: '12px 16px',
                    background: '#fff5f5',
                    border: '1px solid #feb2b2',
                    borderRadius: '6px',
                    color: '#c53030',
                    fontSize: '13px',
                    marginTop: '12px'
                  }}>
                    Error: {error}
                  </div>
                )}
              </>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="chat-input-area">
            <input
              type="text"
              className="chat-input"
              placeholder="Escribe tu pregunta..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isStreaming || !agent}
            />
            <button
              className="btn-send"
              onClick={handleSendMessage}
              disabled={isStreaming || !agent || !inputValue.trim()}
              style={{
                opacity: isStreaming ? 0.6 : 1,
                cursor: isStreaming ? 'not-allowed' : 'pointer'
              }}
            >
              {isStreaming ? 'Streaming...' : 'Send'}
            </button>
          </div>
        </div>
      )}

      {/* Other Tabs Placeholders */}
      {activeTab !== 'chat' && (
        <div style={{
          flex: 1,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#999999'
        }}>
          <p>{tabs.find(t => t.id === activeTab)?.label} tab - Coming soon</p>
        </div>
      )}
    </div>
  )
}
