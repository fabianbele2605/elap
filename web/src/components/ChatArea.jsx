import { useState, useRef, useEffect } from 'react'

export default function ChatArea({ agent, messages, activeTab, onTabChange, onMessageSend }) {
  const [inputValue, setInputValue] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async () => {
    if (!inputValue.trim() || !agent) return

    const userMessage = {
      id: `msg_${Date.now()}`,
      text: inputValue,
      type: 'user',
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }

    onMessageSend(userMessage)
    setInputValue('')
    setLoading(true)

    try {
      const response = await fetch('http://localhost:3000/agents', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agentId: agent.id,
          query: inputValue
        })
      })

      const data = await response.json()

      const assistantMessage = {
        id: `msg_${Date.now()}_asst`,
        text: data.response || 'Sin respuesta',
        type: 'assistant',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }

      onMessageSend(assistantMessage)
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage = {
        id: `msg_${Date.now()}_error`,
        text: 'Error al procesar el mensaje',
        type: 'assistant',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
      onMessageSend(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const tabs = [
    { id: 'chat', label: '💬 Chat' },
    { id: 'dashboard', label: '📊 Dashboard' },
    { id: 'tools', label: '🛠️ Tools' },
    { id: 'knowledge', label: '📚 Knowledge' },
    { id: 'history', label: '📋 History' }
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
            {messages.length === 0 ? (
              <div style={{ textAlign: 'center', color: '#999999', marginTop: '40px' }}>
                <p style={{ fontSize: '14px' }}>No messages yet</p>
                <p style={{ fontSize: '12px', marginTop: '8px' }}>Start a conversation with the agent</p>
              </div>
            ) : (
              messages.map(msg => (
                <div key={msg.id} className={`message ${msg.type}`}>
                  <div>
                    <div className="message-bubble">{msg.text}</div>
                    <span className="message-time">{msg.time}</span>
                  </div>
                </div>
              ))
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
              disabled={loading || !agent}
            />
            <button
              className="btn-send"
              onClick={handleSendMessage}
              disabled={loading || !agent || !inputValue.trim()}
            >
              {loading ? '...' : 'Send'}
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
