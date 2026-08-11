"""Sistema de Auditoría Completo - Registra todas las acciones en la BD"""

import logging
import psycopg2
import psycopg2.extras
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum
import json

logger = logging.getLogger(__name__)


class AuditEventType(Enum):
    """Tipos de eventos auditables"""
    AGENT_EXECUTION = "agent_execution"
    WORKFLOW_START = "workflow_start"
    WORKFLOW_STEP = "workflow_step"
    WORKFLOW_COMPLETE = "workflow_complete"
    WORKFLOW_ERROR = "workflow_error"
    ALERT_TRIGGERED = "alert_triggered"
    DATA_ACCESS = "data_access"
    ERROR = "error"
    API_CALL = "api_call"


class AuditLogger:
    """Registra todas las acciones en auditoría"""

    def __init__(self, db_host="localhost", db_port=5432, db_name="elap_db",
                 db_user="elap_user", db_pass="elap_secure_pass_2026"):
        self.db_host = db_host
        self.db_port = db_port
        self.db_name = db_name
        self.db_user = db_user
        self.db_pass = db_pass
        self.conn = None
        self._init_audit_table()

    def _init_audit_table(self):
        """Crea tabla de auditoría si no existe"""
        try:
            conn = psycopg2.connect(
                host=self.db_host, port=self.db_port,
                database=self.db_name,
                user=self.db_user, password=self.db_pass
            )
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT NOW(),
                    event_type VARCHAR(50) NOT NULL,
                    user_id VARCHAR(255),
                    action VARCHAR(255) NOT NULL,
                    resource_type VARCHAR(100),
                    resource_id VARCHAR(255),
                    details JSONB,
                    status VARCHAR(50),
                    ip_address VARCHAR(50),
                    duration_ms INTEGER,
                    created_at TIMESTAMP DEFAULT NOW()
                );

                CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp DESC);
                CREATE INDEX IF NOT EXISTS idx_audit_event_type ON audit_log(event_type);
                CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_log(user_id);
            """)

            conn.commit()
            cursor.close()
            conn.close()
            logger.info("✅ Tabla de auditoría inicializada")

        except Exception as e:
            logger.error(f"Error inicializando tabla de auditoría: {e}")

    def log_event(
        self,
        event_type: AuditEventType,
        action: str,
        resource_type: str = None,
        resource_id: str = None,
        user_id: str = "system",
        details: Dict[str, Any] = None,
        status: str = "success",
        ip_address: str = None,
        duration_ms: int = None
    ) -> bool:
        """Registra un evento de auditoría

        Args:
            event_type: Tipo de evento
            action: Descripción de la acción
            resource_type: Tipo de recurso afectado
            resource_id: ID del recurso
            user_id: Usuario que realizó la acción
            details: Detalles adicionales en JSON
            status: Estado (success, error, pending)
            ip_address: IP del cliente
            duration_ms: Duración en milisegundos

        Returns:
            True si fue registrado exitosamente
        """
        try:
            conn = psycopg2.connect(
                host=self.db_host, port=self.db_port,
                database=self.db_name,
                user=self.db_user, password=self.db_pass
            )
            cursor = conn.cursor()

            details_json = json.dumps(details or {})

            cursor.execute("""
                INSERT INTO audit_log
                (event_type, action, resource_type, resource_id, user_id, details, status, ip_address, duration_ms)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                event_type.value,
                action,
                resource_type,
                resource_id,
                user_id,
                details_json,
                status,
                ip_address,
                duration_ms
            ))

            conn.commit()
            cursor.close()
            conn.close()

            logger.info(f"📝 Auditoría registrada: {event_type.value} - {action}")
            return True

        except Exception as e:
            logger.error(f"Error registrando auditoría: {e}")
            return False

    def log_workflow_start(self, workflow_id: str, user_id: str = "system", details: Dict = None):
        """Registra inicio de workflow"""
        return self.log_event(
            event_type=AuditEventType.WORKFLOW_START,
            action=f"Workflow iniciado: {workflow_id}",
            resource_type="workflow",
            resource_id=workflow_id,
            user_id=user_id,
            details=details or {}
        )

    def log_workflow_step(self, workflow_id: str, step_id: str, agent_id: str,
                         status: str = "success", duration_ms: int = None, details: Dict = None):
        """Registra paso de workflow"""
        return self.log_event(
            event_type=AuditEventType.WORKFLOW_STEP,
            action=f"Paso ejecutado: {step_id} ({agent_id})",
            resource_type="workflow_step",
            resource_id=f"{workflow_id}:{step_id}",
            details={
                "workflow_id": workflow_id,
                "step_id": step_id,
                "agent_id": agent_id,
                **(details or {})
            },
            status=status,
            duration_ms=duration_ms
        )

    def log_workflow_complete(self, workflow_id: str, status: str, duration_ms: int = None):
        """Registra finalización de workflow"""
        return self.log_event(
            event_type=AuditEventType.WORKFLOW_COMPLETE,
            action=f"Workflow finalizado: {workflow_id}",
            resource_type="workflow",
            resource_id=workflow_id,
            status=status,
            duration_ms=duration_ms
        )

    def log_agent_execution(self, agent_id: str, query: str, status: str = "success",
                           duration_ms: int = None, result_summary: str = None):
        """Registra ejecución de agente"""
        return self.log_event(
            event_type=AuditEventType.AGENT_EXECUTION,
            action=f"Agente ejecutado: {agent_id}",
            resource_type="agent",
            resource_id=agent_id,
            details={
                "query_preview": query[:100] if query else None,
                "result_summary": result_summary
            },
            status=status,
            duration_ms=duration_ms
        )

    def log_alert(self, alert_type: str, kpi: str, current_value: Any, threshold: Any):
        """Registra alerta triggered"""
        return self.log_event(
            event_type=AuditEventType.ALERT_TRIGGERED,
            action=f"Alerta disparada: {alert_type}",
            resource_type="alert",
            resource_id=kpi,
            details={
                "alert_type": alert_type,
                "kpi": kpi,
                "current_value": current_value,
                "threshold": threshold
            },
            status="warning"
        )

    def log_api_call(self, endpoint: str, method: str, status_code: int,
                    duration_ms: int = None, user_id: str = "anonymous"):
        """Registra llamada a API"""
        return self.log_event(
            event_type=AuditEventType.API_CALL,
            action=f"{method} {endpoint}",
            resource_type="api",
            resource_id=endpoint,
            user_id=user_id,
            details={"method": method, "status_code": status_code},
            status="success" if status_code < 400 else "error",
            duration_ms=duration_ms
        )

    def log_error(self, error_type: str, error_msg: str, context: Dict = None):
        """Registra error"""
        return self.log_event(
            event_type=AuditEventType.ERROR,
            action=f"Error: {error_type}",
            details={
                "error_type": error_type,
                "error_message": error_msg,
                **(context or {})
            },
            status="error"
        )

    def get_audit_log(self, limit: int = 100, event_type: str = None,
                     user_id: str = None, days: int = 7) -> list:
        """Obtiene log de auditoría con filtros"""
        try:
            conn = psycopg2.connect(
                host=self.db_host, port=self.db_port,
                database=self.db_name,
                user=self.db_user, password=self.db_pass
            )
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            query = "SELECT * FROM audit_log WHERE created_at > NOW() - INTERVAL '%d days'" % days
            params = []

            if event_type:
                query += " AND event_type = %s"
                params.append(event_type)

            if user_id:
                query += " AND user_id = %s"
                params.append(user_id)

            query += " ORDER BY created_at DESC LIMIT %s"
            params.append(limit)

            cursor.execute(query, params)
            logs = cursor.fetchall()

            cursor.close()
            conn.close()

            # Convertir datetime a string
            result = []
            for log in logs:
                log_dict = dict(log)
                if log_dict.get('timestamp'):
                    log_dict['timestamp'] = log_dict['timestamp'].isoformat()
                if log_dict.get('created_at'):
                    log_dict['created_at'] = log_dict['created_at'].isoformat()
                result.append(log_dict)

            return result

        except Exception as e:
            logger.error(f"Error obteniendo audit log: {e}")
            return []

    def get_workflow_audit(self, workflow_id: str) -> Dict[str, Any]:
        """Obtiene auditoría completa de un workflow"""
        try:
            conn = psycopg2.connect(
                host=self.db_host, port=self.db_port,
                database=self.db_name,
                user=self.db_user, password=self.db_pass
            )
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            # Obtener eventos del workflow
            cursor.execute("""
                SELECT * FROM audit_log
                WHERE resource_type IN ('workflow', 'workflow_step')
                AND resource_id LIKE %s
                ORDER BY created_at ASC
            """, (f"{workflow_id}%",))

            events = cursor.fetchall()

            cursor.close()
            conn.close()

            # Convertir datetime a string
            result_events = []
            for event in events:
                event_dict = dict(event)
                if event_dict.get('timestamp'):
                    event_dict['timestamp'] = event_dict['timestamp'].isoformat()
                if event_dict.get('created_at'):
                    event_dict['created_at'] = event_dict['created_at'].isoformat()
                result_events.append(event_dict)

            return {
                "workflow_id": workflow_id,
                "events": result_events,
                "total_events": len(result_events)
            }

        except Exception as e:
            logger.error(f"Error obteniendo audit de workflow: {e}")
            return {}

    def get_statistics(self, days: int = 7) -> Dict[str, Any]:
        """Obtiene estadísticas de auditoría"""
        try:
            conn = psycopg2.connect(
                host=self.db_host, port=self.db_port,
                database=self.db_name,
                user=self.db_user, password=self.db_pass
            )
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            # Estadísticas por tipo de evento
            cursor.execute("""
                SELECT
                    event_type,
                    COUNT(*) as count,
                    COUNT(CASE WHEN status = 'error' THEN 1 END) as errors,
                    AVG(duration_ms) as avg_duration_ms
                FROM audit_log
                WHERE created_at > NOW() - INTERVAL '%d days'
                GROUP BY event_type
            """ % days)

            stats = cursor.fetchall()

            cursor.close()
            conn.close()

            return {
                "period_days": days,
                "statistics": [dict(s) for s in stats]
            }

        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {}
