import { useState, useCallback, useEffect } from 'react';
import { apiCall } from '../services/api';

export interface ConversationMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  agent_name?: string;
  timestamp: string;
  metadata?: any;
}

export interface Conversation {
  id: string;
  title: string;
  agent_name: string;
  agent_id?: string;
  created_at: string;
  updated_at: string;
  messages?: ConversationMessage[];
  message_count?: number;
}

export function useConversation() {
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentMessages, setCurrentMessages] = useState<ConversationMessage[]>([]);
  const [loading, setLoading] = useState(false);

  // Crear nueva conversación
  const createConversation = useCallback(async (agentName: string, agentId?: string) => {
    try {
      setLoading(true);
      const response = await apiCall('POST', '/conversations', {
        agent_name: agentName,
        agent_id: agentId || 'unknown',
        title: `Chat con ${agentName}`
      });

      const convId = response.id;
      setCurrentConversationId(convId);
      setCurrentMessages([]);

      // Guardar en localStorage
      localStorage.setItem('currentConversationId', convId);
      localStorage.setItem('currentAgentName', agentName);

      // Recargar lista
      await loadConversations();

      return convId;
    } catch (error) {
      console.error('Error creando conversación:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  // Cargar lista de conversaciones
  const loadConversations = useCallback(async () => {
    try {
      const response = await apiCall('GET', '/conversations', undefined);
      setConversations(response.conversations || []);
    } catch (error) {
      console.error('Error cargando conversaciones:', error);
    }
  }, []);

  // Cargar conversación específica
  const loadConversation = useCallback(async (convId: string) => {
    try {
      setLoading(true);
      const response = await apiCall('GET', `/conversations/${convId}`, undefined);

      setCurrentConversationId(convId);
      setCurrentMessages(response.messages || []);

      // Guardar en localStorage
      localStorage.setItem('currentConversationId', convId);

      return response;
    } catch (error) {
      console.error('Error cargando conversación:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  // Agregar mensaje a conversación
  const addMessage = useCallback(async (
    role: 'user' | 'assistant',
    content: string,
    agentName?: string,
    metadata?: any
  ) => {
    if (!currentConversationId) {
      console.error('No hay conversación activa');
      return;
    }

    try {
      await apiCall('POST', `/conversations/${currentConversationId}/messages`, {
        role,
        content,
        agent_name: agentName,
        metadata
      });

      // Actualizar lista local
      const newMessage: ConversationMessage = {
        id: Math.random().toString(36),
        role,
        content,
        agent_name: agentName,
        timestamp: new Date().toISOString(),
        metadata
      };

      setCurrentMessages(prev => [...prev, newMessage]);
    } catch (error) {
      console.error('Error agregando mensaje:', error);
      throw error;
    }
  }, [currentConversationId]);

  // Eliminar conversación
  const deleteConversation = useCallback(async (convId: string) => {
    try {
      await apiCall('DELETE', `/conversations/${convId}`, undefined);

      // Si es la actual, crear una nueva
      if (currentConversationId === convId) {
        setCurrentConversationId(null);
        setCurrentMessages([]);
        localStorage.removeItem('currentConversationId');
      }

      // Recargar lista
      await loadConversations();
    } catch (error) {
      console.error('Error eliminando conversación:', error);
      throw error;
    }
  }, [currentConversationId]);

  // Restaurar conversación desde localStorage
  useEffect(() => {
    const savedConvId = localStorage.getItem('currentConversationId');
    if (savedConvId && !currentConversationId) {
      loadConversation(savedConvId).catch(() => {
        // Si no existe, limpiar localStorage
        localStorage.removeItem('currentConversationId');
      });
    }
  }, []);

  // Cargar lista al montar
  useEffect(() => {
    loadConversations();
    // 🛑 NO crear conversación automáticamente - solo crear cuando se envíe el primer mensaje
  }, [loadConversations]);

  return {
    currentConversationId,
    currentMessages,
    conversations,
    loading,
    createConversation,
    loadConversation,
    loadConversations,
    addMessage,
    deleteConversation,
    setCurrentConversationId
  };
}
