import { useState } from 'react'

export default function Sidebar({ agents, activeAgentId, onSelectAgent, systemStatus }) {
  const [searchQuery, setSearchQuery] = useState('')

  const filteredAgents = agents.filter(agent =>
    agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    agent.role.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const agentInitials = {
    Sales: 'SA',
    IT: 'IT',
    HR: 'HR',
    Analytics: 'AN',
    Research: 'RE',
    Finance: 'FI',
    Support: 'SU',
    Legal: 'LE'
  }

  return (
    <div className="sidebar-agents">
      <div className="sidebar-header">
        <span style={{ width: '24px', height: '24px', borderRadius: '6px', background: '#0052cc', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontSize: '12px', fontWeight: '700' }}>E</span>
        <span>ELAP</span>
        <span style={{ marginLeft: 'auto', fontFamily: 'monospace', fontSize: '10px', color: '#999999' }}>v1.4.0</span>
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
            <span className="agent-item-icon" style={{
              width: '32px',
              height: '32px',
              borderRadius: '6px',
              background: activeAgentId === agent.id ? '#0052cc' : '#f0f0f0',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '11px',
              fontWeight: '700',
              color: activeAgentId === agent.id ? 'white' : '#666666',
              flexShrink: 0
            }}>
              {agentInitials[agent.role] || 'AG'}
            </span>
            <div className="agent-item-content">
              <span className="agent-item-name">{agent.name}</span>
              <span className="agent-item-role">{agent.role}</span>
              <span className="agent-item-status">Online</span>
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
            <span>Rust Core (localhost:3000)</span>
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
