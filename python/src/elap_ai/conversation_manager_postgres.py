"""Gestor de historial de conversaciones con PostgreSQL
Almacena y recupera chats usando PostgreSQL (producción)
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid

logger = logging.getLogger(__name__)


class ConversationManagerPostgres:
    """Gestiona historiales de conversaciones con PostgreSQL"""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        database: str = "elap_db",
        user: str = "elap_user",
        password: str = "elap_secure_pass_2026"
    ):
        """Inicializa gestor con PostgreSQL"""
        self.connection_params = {
            "host": host,
            "port": port,
            "database": database,
            "user": user,
            "password": password
        }
        self._test_connection()
        logger.info(f"✅ ConversationManagerPostgres initialized: {host}:{port}/{database}")

    def _get_connection(self):
        """Obtiene conexión a PostgreSQL"""
        return psycopg2.connect(**self.connection_params)

    def _test_connection(self):
        """Verifica conexión a BD"""
        try:
            conn = self._get_connection()
            conn.close()
            logger.info("✅ PostgreSQL conexión exitosa")
        except Exception as e:
            logger.error(f"❌ Error conectando a PostgreSQL: {e}")
            raise

    def create_conversation(self, agent_id: str, agent_name: str, title: Optional[str] = None) -> str:
        """Crea nueva conversación y retorna ID"""
        conv_id = str(uuid.uuid4())
        if not title:
            title = f"Chat con {agent_name} - {datetime.now().strftime('%d/%m %H:%M')}"

        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO conversations (id, title, agent_id, agent_name, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (conv_id, title, agent_id, agent_name, datetime.now(), datetime.now()))

            conn.commit()
            cursor.close()
            conn.close()

            logger.info(f"✅ Conversation created: {conv_id} ({agent_name})")
            return conv_id
        except Exception as e:
            logger.error(f"❌ Error creando conversación: {e}")
            raise

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        agent_name: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """Agrega mensaje a conversación"""
        msg_id = str(uuid.uuid4())

        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            metadata_json = json.dumps(metadata) if metadata else None

            cursor.execute("""
                INSERT INTO messages (id, conversation_id, role, content, agent_name, timestamp, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (msg_id, conversation_id, role, content, agent_name, datetime.now(), metadata_json))

            # Actualizar timestamp de conversación
            cursor.execute("""
                UPDATE conversations SET updated_at = %s WHERE id = %s
            """, (datetime.now(), conversation_id))

            conn.commit()
            cursor.close()
            conn.close()

            return msg_id
        except Exception as e:
            logger.error(f"❌ Error agregando mensaje: {e}")
            raise

    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene conversación con todos sus mensajes"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # Obtener conversación
            cursor.execute("SELECT * FROM conversations WHERE id = %s", (conversation_id,))
            conv = cursor.fetchone()

            if not conv:
                return None

            # Obtener mensajes
            cursor.execute("""
                SELECT id, role, content, agent_name, timestamp, metadata
                FROM messages
                WHERE conversation_id = %s
                ORDER BY timestamp ASC
            """, (conversation_id,))

            messages = []
            for row in cursor.fetchall():
                msg = dict(row)
                if msg.get('metadata'):
                    try:
                        msg['metadata'] = json.loads(msg['metadata'])
                    except:
                        pass
                # Convertir timestamp a ISO string
                if 'timestamp' in msg and msg['timestamp']:
                    if hasattr(msg['timestamp'], 'isoformat'):
                        msg['timestamp'] = msg['timestamp'].isoformat()
                    else:
                        msg['timestamp'] = str(msg['timestamp'])
                messages.append(msg)

            conv_data = dict(conv)
            # Convertir UUID a string
            if 'id' in conv_data and conv_data['id']:
                conv_data['id'] = str(conv_data['id'])
            # Convertir fechas a ISO strings
            if 'created_at' in conv_data and conv_data['created_at']:
                if hasattr(conv_data['created_at'], 'isoformat'):
                    conv_data['created_at'] = conv_data['created_at'].isoformat()
                else:
                    conv_data['created_at'] = str(conv_data['created_at'])
            if 'updated_at' in conv_data and conv_data['updated_at']:
                if hasattr(conv_data['updated_at'], 'isoformat'):
                    conv_data['updated_at'] = conv_data['updated_at'].isoformat()
                else:
                    conv_data['updated_at'] = str(conv_data['updated_at'])

            conv_data['messages'] = messages

            cursor.close()
            conn.close()

            return conv_data
        except Exception as e:
            logger.error(f"❌ Error obteniendo conversación: {e}")
            return None

    def list_conversations(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Lista últimas conversaciones"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute("""
                SELECT id, title, agent_name, created_at, updated_at,
                       (SELECT COUNT(*) FROM messages WHERE conversation_id = conversations.id) as message_count
                FROM conversations
                ORDER BY updated_at DESC
                LIMIT %s
            """, (limit,))

            conversations = []
            for row in cursor.fetchall():
                conv = dict(row)
                # Convertir UUID a string
                if 'id' in conv and conv['id']:
                    conv['id'] = str(conv['id'])
                # Convertir fechas a ISO strings
                if 'created_at' in conv and conv['created_at']:
                    if hasattr(conv['created_at'], 'isoformat'):
                        conv['created_at'] = conv['created_at'].isoformat()
                    else:
                        conv['created_at'] = str(conv['created_at'])
                if 'updated_at' in conv and conv['updated_at']:
                    if hasattr(conv['updated_at'], 'isoformat'):
                        conv['updated_at'] = conv['updated_at'].isoformat()
                    else:
                        conv['updated_at'] = str(conv['updated_at'])
                conversations.append(conv)

            cursor.close()
            conn.close()

            return conversations
        except Exception as e:
            logger.error(f"❌ Error listando conversaciones: {e}")
            return []

    def get_recent_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtiene conversaciones recientes para sidebar"""
        convs = self.list_conversations(limit)
        return [
            {
                "id": str(c["id"]),
                "title": c["title"],
                "agent_name": c["agent_name"],
                "message_count": c["message_count"],
                "updated_at": c["updated_at"]  # Ya convertido a string en list_conversations
            }
            for c in convs
        ]

    def delete_conversation(self, conversation_id: str) -> bool:
        """Elimina conversación (cascada elimina mensajes)"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("DELETE FROM conversations WHERE id = %s", (conversation_id,))

            conn.commit()
            cursor.close()
            conn.close()

            logger.info(f"✅ Conversation deleted: {conversation_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Error eliminando conversación: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas del historial"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute("SELECT COUNT(*) as count FROM conversations")
            total_convs = cursor.fetchone()['count']

            cursor.execute("SELECT COUNT(*) as count FROM messages")
            total_msgs = cursor.fetchone()['count']

            cursor.execute("""
                SELECT agent_name, COUNT(*) as count
                FROM conversations
                GROUP BY agent_name
                ORDER BY count DESC
            """)
            by_agent = {row['agent_name']: row['count'] for row in cursor.fetchall()}

            cursor.close()
            conn.close()

            return {
                "total_conversations": total_convs,
                "total_messages": total_msgs,
                "conversations_by_agent": by_agent
            }
        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas: {e}")
            return {}
