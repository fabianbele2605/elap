import React from 'react';
import { Conversation } from '../hooks/useConversation';
import './ConversationHistory.css';

interface ConversationHistoryProps {
  conversations: Conversation[];
  currentConversationId: string | null;
  onSelectConversation: (convId: string) => void;
  onDeleteConversation: (convId: string) => void;
  onNewConversation: () => void;
  loading: boolean;
}

export function ConversationHistory({
  conversations,
  currentConversationId,
  onSelectConversation,
  onDeleteConversation,
  onNewConversation,
  loading
}: ConversationHistoryProps) {
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    if (date.toDateString() === today.toDateString()) {
      return date.toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' });
    } else if (date.toDateString() === yesterday.toDateString()) {
      return 'Ayer';
    } else {
      return date.toLocaleDateString('es-CO', { month: 'short', day: 'numeric' });
    }
  };

  return (
    <div className="conversation-history">
      <div className="conv-header">
        <h3>💬 Conversaciones</h3>
        <button
          className="btn-new-conv"
          onClick={onNewConversation}
          title="Nueva conversación"
        >
          ➕
        </button>
      </div>

      {loading && <div className="loading">Cargando...</div>}

      {conversations.length === 0 && !loading && (
        <div className="empty-state">
          <p>📭 Sin conversaciones</p>
          <small>Inicia una nueva para comenzar</small>
        </div>
      )}

      <div className="conv-list">
        {conversations.map((conv) => (
          <div
            key={conv.id}
            className={`conv-item ${
              currentConversationId === conv.id ? 'active' : ''
            }`}
            onClick={() => onSelectConversation(conv.id)}
          >
            <div className="conv-content">
              <div className="conv-title">{conv.title}</div>
              <div className="conv-meta">
                <span className="conv-agent">🤖 {conv.agent_name}</span>
                <span className="conv-count">
                  {conv.message_count || 0} mensajes
                </span>
              </div>
              <div className="conv-time">
                {formatDate(conv.updated_at)}
              </div>
            </div>

            <button
              className="btn-delete"
              onClick={(e) => {
                e.stopPropagation();
                if (
                  confirm(`¿Eliminar "${conv.title}"?`)
                ) {
                  onDeleteConversation(conv.id);
                }
              }}
              title="Eliminar"
            >
              🗑️
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
