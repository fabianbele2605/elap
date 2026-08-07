import { useState } from 'react'

export default function Sidebar({ agents, activeAgentId, onSelectAgent, systemStatus }) {
  const [searchQuery, setSearchQuery] = useState('')

  const filteredAgents = agents.filter(agent =>
    agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    agent.role.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const agentIcons = {
    Sales: '📈',
    IT: '🛠️',
    HR: '👥',
    Analytics: '📊',
    Research: '🔬',
    Finance: '💰',
    Support: '🎧',
    Legal: '⚖️'
  }

  return (
    <div className="sidebar-agents">
      <div className="sidebar-header">
        <span>⚡</span>
        <span>Agents</span>
      </div>

      <input
        type="text"
        className="agent-search"
        placeholder="Search agents..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
      />

      <div className="agent-list">
        {filteredAgents.map(agent => (
          <div
            key={agent.id}
            className={`agent-item ${activeAgentId === agent.id ? 'active' : ''}`}
            onClick={() => onSelectAgent(agent.id)}
          >
            <span className="agent-item-icon">
              {agentIcons[agent.role] || '🤖'}
            </span>
            <div className="agent-item-content">
              <span className="agent-item-name">{agent.name}</span>
              <span className="agent-item-role">{agent.role}</span>
              <span className="agent-item-status">✅ Online</span>
            </div>
            <div className="status-dot"></div>
          </div>
        ))}
      </div>

      <div className="sidebar-footer">
        <button className="btn-new-agent">+ NEW AGENT</button>
        <div className="connection-status">
          <div className="status-item">
            <div className="status-indicator"></div>
            <span>Rust Core (3000)</span>
          </div>
          <div className="status-item">
            <div className="status-indicator"></div>
            <span>Python gRPC (50051)</span>
          </div>
          <div className="status-item">
            <div className="status-indicator"></div>
            <span>Ollama (11434)</span>
          </div>
        </div>
      </div>
    </div>
  )
}
