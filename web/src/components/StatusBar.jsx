export default function StatusBar({ systemStatus }) {
  const getCurrentTime = () => {
    return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className="status-bar">
      <div className="status-section">
        <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
          <div className="status-indicator"></div>
          <span>Rust Core (3000)</span>
        </div>
        <span style={{ color: '#999999' }}>|</span>
        <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
          <div className="status-indicator"></div>
          <span>Python gRPC (50051)</span>
        </div>
        <span style={{ color: '#999999' }}>|</span>
        <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
          <div className="status-indicator"></div>
          <span>Ollama (11434)</span>
        </div>
      </div>

      <div className="status-section">
        <span>CPU: 45%</span>
        <span style={{ color: '#999999' }}>|</span>
        <span>RAM: 2.3GB / 8GB</span>
        <span style={{ color: '#999999' }}>|</span>
        <span>Disk: 340GB / 1TB</span>
      </div>

      <div className="status-section">
        <span>👤 Admin User</span>
        <span style={{ color: '#999999' }}>|</span>
        <span>🔔 2</span>
        <span style={{ color: '#999999' }}>|</span>
        <span>🕐 {getCurrentTime()}</span>
        <span style={{ color: '#999999' }}>|</span>
        <span>🔋 92%</span>
      </div>
    </div>
  )
}
