import React, { useState, useEffect, useRef } from 'react';
import '../styles/StreamingResponse.css';

export default function StreamingResponse({ agentId, query, onClose }) {
  const [response, setResponse] = useState('');
  const [status, setStatus] = useState('conectando');
  const [progress, setProgress] = useState(0);
  const wsRef = useRef(null);

  useEffect(() => {
    // Conectar WebSocket
    const ws = new WebSocket(`ws://localhost:3000/agents/${agentId}/execute/stream`);

    ws.onopen = () => {
      console.log('✅ WebSocket conectado');
      setStatus('enviando_query');
      // Enviar query
      ws.send(query);
    };

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);

      switch (msg.tipo) {
        case 'streaming_iniciado':
          setStatus('preparado');
          break;

        case 'procesando':
          setStatus('procesando');
          break;

        case 'token':
          // Agregar token a la respuesta
          setResponse(prev => prev + msg.datos.chunk + ' ');
          setProgress(msg.datos.progreso);
          break;

        case 'streaming_completado':
          setStatus('completo');
          setProgress(100);
          break;

        case 'error':
          setStatus('error');
          setResponse(msg.datos.mensaje);
          break;

        default:
          console.log('Evento:', msg.tipo);
      }
    };

    ws.onerror = (error) => {
      console.error('❌ Error WebSocket:', error);
      setStatus('error');
      setResponse('Error de conexión con el servidor');
    };

    ws.onclose = () => {
      console.log('WebSocket cerrado');
    };

    wsRef.current = ws;

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [agentId, query]);

  return (
    <div className="streaming-response">
      <div className="sr-header">
        <h3>🔄 Streaming en vivo</h3>
        <button className="sr-close" onClick={onClose}>✕</button>
      </div>

      <div className="sr-status">
        <span className={`status-badge ${status}`}>{status}</span>
        {progress > 0 && progress < 100 && (
          <div className="sr-progress">
            <div className="sr-progress-bar" style={{ width: `${progress}%` }}></div>
          </div>
        )}
      </div>

      <div className="sr-content">
        {response ? (
          <p>{response}</p>
        ) : (
          <p className="sr-placeholder">Esperando respuesta del agente...</p>
        )}
      </div>

      <div className="sr-footer">
        {status === 'completo' ? (
          <span>✅ Respuesta completada</span>
        ) : (
          <span>⏳ {status === 'error' ? '❌ Error' : 'Procesando...'}</span>
        )}
      </div>
    </div>
  );
}
