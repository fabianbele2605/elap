export default function StreamingMessage({ text, progress, isStreaming, timestamp }) {
  return (
    <div className="message assistant">
      <div>
        <div className="message-bubble">
          <div style={{ marginBottom: isStreaming ? '8px' : '0' }}>
            {text || (isStreaming ? 'Procesando...' : 'Sin respuesta')}
          </div>

          {isStreaming && (
            <>
              <div className="streaming-dots">
                <span>Generando respuesta</span>
                <span style={{
                  display: 'inline-flex',
                  gap: '3px',
                  marginLeft: '6px'
                }}>
                  <span style={{
                    width: '3px',
                    height: '3px',
                    background: '#0052cc',
                    borderRadius: '50%',
                    animation: 'pulse 1.4s infinite'
                  }}></span>
                  <span style={{
                    width: '3px',
                    height: '3px',
                    background: '#0052cc',
                    borderRadius: '50%',
                    animation: 'pulse 1.4s infinite 0.2s'
                  }}></span>
                  <span style={{
                    width: '3px',
                    height: '3px',
                    background: '#0052cc',
                    borderRadius: '50%',
                    animation: 'pulse 1.4s infinite 0.4s'
                  }}></span>
                </span>
              </div>

              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{
                    width: `${progress}%`,
                    transition: 'width 0.2s ease-in-out'
                  }}
                ></div>
              </div>
            </>
          )}
        </div>
        <span className="message-time">{timestamp}</span>
      </div>

      <style>{`
        @keyframes pulse {
          0%, 60%, 100% { opacity: 0.3; }
          30% { opacity: 1; }
        }
      `}</style>
    </div>
  )
}
