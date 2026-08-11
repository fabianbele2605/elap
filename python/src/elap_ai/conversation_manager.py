"""Gestor de historial de conversaciones
Almacena y recupera chats usando SQLite
"""

import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class ConversationManager:
    """Gestiona historiales de conversaciones con persistencia SQLite"""

    def __init__(self, db_path: Optional[str] = None):
        """Inicializa BD de conversaciones"""
        if db_path is None:
            # Usar ruta absoluta por defecto
            db_path = "/tmp/elap_conversations.db"

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        logger.info(f"ConversationManager initialized: {self.db_path}")

    def _init_db(self):
        """Crea tablas si no existen"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Tabla de conversaciones
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    agent_id TEXT,
                    agent_name TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    theme TEXT DEFAULT 'andina_foods'
                )
            """)

            # Tabla de mensajes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    agent_name TEXT,
                    timestamp TEXT NOT NULL,
                    metadata TEXT,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
                )
            """)

            # Crear índices para búsqueda rápida
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_created
                ON conversations(created_at DESC)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_conversation
                ON messages(conversation_id, timestamp)
            """)

            conn.commit()
            logger.info("✅ Database initialized")

    def create_conversation(self, agent_id: str, agent_name: str, title: Optional[str] = None) -> str:
        """Crea nueva conversación y retorna ID"""
        import uuid
        conv_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        # Si no hay título, usar el nombre del agente + timestamp
        if not title:
            title = f"Chat con {agent_name} - {datetime.now().strftime('%d/%m %H:%M')}"

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO conversations (id, title, agent_id, agent_name, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (conv_id, title, agent_id, agent_name, now, now))
            conn.commit()

        logger.info(f"✅ Conversation created: {conv_id} ({agent_name})")
        return conv_id

    def add_message(self, conversation_id: str, role: str, content: str, agent_name: Optional[str] = None, metadata: Optional[Dict] = None) -> str:
        """Agrega mensaje a conversación"""
        import uuid
        msg_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        metadata_json = json.dumps(metadata) if metadata else None

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Agregar mensaje
            cursor.execute("""
                INSERT INTO messages (id, conversation_id, role, content, agent_name, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (msg_id, conversation_id, role, content, agent_name, now, metadata_json))

            # Actualizar timestamp de conversación
            cursor.execute("""
                UPDATE conversations SET updated_at = ? WHERE id = ?
            """, (now, conversation_id))

            conn.commit()

        return msg_id

    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene conversación con todos sus mensajes"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Obtener metadata de conversación
            cursor.execute("SELECT * FROM conversations WHERE id = ?", (conversation_id,))
            conv_row = cursor.fetchone()

            if not conv_row:
                return None

            conv_data = dict(conv_row)

            # Obtener mensajes
            cursor.execute("""
                SELECT id, role, content, agent_name, timestamp, metadata
                FROM messages
                WHERE conversation_id = ?
                ORDER BY timestamp ASC
            """, (conversation_id,))

            messages = []
            for row in cursor.fetchall():
                msg = dict(row)
                if msg['metadata']:
                    msg['metadata'] = json.loads(msg['metadata'])
                messages.append(msg)

            conv_data['messages'] = messages
            return conv_data

    def list_conversations(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Lista últimas conversaciones (con resumen)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, title, agent_name, created_at, updated_at,
                       (SELECT COUNT(*) FROM messages WHERE conversation_id = conversations.id) as message_count
                FROM conversations
                ORDER BY updated_at DESC
                LIMIT ?
            """, (limit,))

            conversations = []
            for row in cursor.fetchall():
                conv = dict(row)
                conversations.append(conv)

            return conversations

    def get_recent_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtiene conversaciones recientes para mostrar en sidebar"""
        convs = self.list_conversations(limit)
        return [
            {
                "id": c["id"],
                "title": c["title"],
                "agent_name": c["agent_name"],
                "message_count": c["message_count"],
                "updated_at": c["updated_at"]
            }
            for c in convs
        ]

    def delete_conversation(self, conversation_id: str) -> bool:
        """Elimina conversación y sus mensajes"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Eliminar mensajes
            cursor.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))

            # Eliminar conversación
            cursor.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))

            conn.commit()
            logger.info(f"✅ Conversation deleted: {conversation_id}")
            return True

    def search_conversations(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Busca en título de conversaciones"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, title, agent_name, created_at, updated_at
                FROM conversations
                WHERE title LIKE ? OR agent_name LIKE ?
                ORDER BY updated_at DESC
                LIMIT ?
            """, (f"%{query}%", f"%{query}%", limit))

            return [dict(row) for row in cursor.fetchall()]

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas del historial"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM conversations")
            total_convs = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM messages")
            total_msgs = cursor.fetchone()[0]

            cursor.execute("""
                SELECT agent_name, COUNT(*) as count
                FROM conversations
                GROUP BY agent_name
                ORDER BY count DESC
            """)
            by_agent = dict(cursor.fetchall())

            return {
                "total_conversations": total_convs,
                "total_messages": total_msgs,
                "conversations_by_agent": by_agent
            }
