import { useState, useEffect } from 'react'
import './App.css'
import Sidebar from './components/Sidebar'
import ChatArea from './components/ChatArea'
import PropertiesPanel from './components/PropertiesPanel'
import StatusBar from './components/StatusBar'

function App() {
  const [agents, setAgents] = useState([])
  const [activeAgentId, setActiveAgentId] = useState(null)
  const [messages, setMessages] = useState([])
  const [activeTab, setActiveTab] = useState('chat')
  const [loading, setLoading] = useState(true)
  const [systemStatus, setSystemStatus] = useState({
    rustCore: false,
    pythonGrpc: false,
    ollama: false,
    cpu: 0,
    ram: 0
  })

  const fetchAgents = async () => {
    try {
      const response = await fetch('http://localhost:3000/agents')
      const data = await response.json()
      const transformed = data.agentes.map(agent => ({
        id: agent.id,
        name: agent.nombre,
        role: agent.rol,
        model: agent.modelo,
        status: 'online'
      }))
      setAgents(transformed)
      if (transformed.length > 0 && !activeAgentId) {
        setActiveAgentId(transformed[0].id)
      }
      setLoading(false)
    } catch (error) {
      console.error('Error fetching agents:', error)
      setLoading(false)
    }
  }

  const checkSystemStatus = async () => {
    try {
      const rustCheck = fetch('http://localhost:3000/agents').then(() => true).catch(() => false)
      const ollamaCheck = fetch('http://localhost:11434/api/tags').then(() => true).catch(() => false)

      const [rust, ollama] = await Promise.all([rustCheck, ollamaCheck])
      setSystemStatus(prev => ({
        ...prev,
        rustCore: rust,
        ollama: ollama
      }))
    } catch (error) {
      console.error('Error checking system status:', error)
    }
  }

  useEffect(() => {
    fetchAgents()
    checkSystemStatus()
    const interval = setInterval(checkSystemStatus, 5000)
    return () => clearInterval(interval)
  }, [])

  const activeAgent = agents.find(a => a.id === activeAgentId)

  return (
    <div className="elap-desktop">
      {/* Title Bar */}
      <div className="title-bar">
        <div className="title-bar-left">
          <span>ELAP v1.4.0</span>
          <span>—</span>
          <span>Enterprise Local AI Platform</span>
        </div>
        <div className="title-bar-right">
          <div className="window-control">−</div>
          <div className="window-control">□</div>
          <div className="window-control">✕</div>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        {/* Left Sidebar */}
        <Sidebar
          agents={agents}
          activeAgentId={activeAgentId}
          onSelectAgent={setActiveAgentId}
          systemStatus={systemStatus}
        />

        {/* Center Chat Area */}
        <ChatArea
          agent={activeAgent}
          messages={messages}
          activeTab={activeTab}
          onTabChange={setActiveTab}
          onMessageSend={(msg) => setMessages([...messages, msg])}
        />

        {/* Right Properties Panel */}
        <PropertiesPanel
          agent={activeAgent}
          loading={loading}
        />
      </div>

      {/* Bottom Status Bar */}
      <StatusBar systemStatus={systemStatus} />
    </div>
  )
}

export default App
