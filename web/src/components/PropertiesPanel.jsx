export default function PropertiesPanel({ agent, loading }) {
  if (!agent) {
    return (
      <div className="properties-panel">
        <div className="properties-header">PROPERTIES</div>
        <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#999999' }}>
          <p>Select an agent to view properties</p>
        </div>
      </div>
    )
  }

  return (
    <div className="properties-panel">
      <div className="properties-header">PROPERTIES</div>

      {/* Agent Details */}
      <div className="property-card">
        <div className="property-card-title">AGENT DETAILS</div>
        <div className="property-rows">
          <div className="property-row">
            <span className="property-label">ID</span>
            <span className="property-value">{agent.id}</span>
          </div>
          <div className="property-row">
            <span className="property-label">Role</span>
            <span className="property-value">{agent.role}</span>
          </div>
          <div className="property-row">
            <span className="property-label">Model</span>
            <span className="property-value">{agent.model}</span>
          </div>
          <div className="property-row">
            <span className="property-label">Status</span>
            <span className="property-value">✅ Online</span>
          </div>
          <div className="property-row">
            <span className="property-label">Availability</span>
            <span className="property-value">24/7</span>
          </div>
        </div>
      </div>

      {/* Tools */}
      <div className="property-card">
        <div className="property-card-title">TOOLS</div>
        <div className="property-rows">
          <div className="property-row">
            <span className="property-label">Web Search</span>
            <span className="property-value">✓</span>
          </div>
          <div className="property-row">
            <span className="property-label">Data Analysis</span>
            <span className="property-value">✓</span>
          </div>
          <div className="property-row">
            <span className="property-label">Report Generation</span>
            <span className="property-value">✓</span>
          </div>
          <div className="property-row">
            <span className="property-label">Database Query</span>
            <span className="property-value">✓</span>
          </div>
        </div>
      </div>

      {/* Knowledge Sources */}
      <div className="property-card">
        <div className="property-card-title">KNOWLEDGE SOURCES</div>
        <div className="property-rows">
          <div className="property-row">
            <span className="property-label">Sales Database</span>
            <span className="property-value">Live</span>
          </div>
          <div className="property-row">
            <span className="property-label">Q3 Report</span>
            <span className="property-value">Cached</span>
          </div>
          <div className="property-row">
            <span className="property-label">Market Data</span>
            <span className="property-value">Updated</span>
          </div>
          <div className="property-row">
            <span className="property-label">Company Docs</span>
            <span className="property-value">Vectorized</span>
          </div>
        </div>
      </div>
    </div>
  )
}
