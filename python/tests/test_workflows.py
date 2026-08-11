"""Tests exhaustivos para Workflows - Integración de agentes"""

import pytest
import asyncio
from datetime import datetime

# Importar los módulos a testear
import sys
sys.path.insert(0, '/home/fabian/Escritorio/agenteC/python/src')

from elap_ai.workflow_executor import WorkflowExecutor
from elap_ai.alert_manager import AlertManager
from elap_ai.audit_logger import AuditLogger, AuditEventType


class TestAlertManager:
    """Tests para AlertManager"""

    def test_cartera_vencida_alert(self):
        """Test: Alerta se dispara cuando cartera vencida > $100M"""
        alert_mgr = AlertManager()

        # Cartera vencida: $761M > $100M threshold
        alert_mgr.check_cartera_vencida(761_274_180.0)

        assert len(alert_mgr.alerts) == 1
        assert alert_mgr.alerts[0].level.value == "🚨 CRÍTICA"
        assert "cartera_vencida" in alert_mgr.alerts[0].kpi

    def test_concentracion_clientes_alert(self):
        """Test: Alerta cuando un cliente concentra > 25%"""
        alert_mgr = AlertManager()

        # Concentración: 25.3% > 25% threshold
        alert_mgr.check_concentracion_clientes(25.3)

        assert len(alert_mgr.alerts) == 1
        assert alert_mgr.alerts[0].level.value == "⚠️ MEDIA"

    def test_proyectos_riesgo_alert(self):
        """Test: Alerta cuando hay 4 proyectos en riesgo > 2"""
        alert_mgr = AlertManager()

        # 4 proyectos > 2 threshold
        alert_mgr.check_proyectos_riesgo(4)

        assert len(alert_mgr.alerts) == 1
        assert alert_mgr.alerts[0].current_value == 4

    def test_clear_old_alerts(self):
        """Test: Limpiar alertas antiguas"""
        alert_mgr = AlertManager()

        # Agregar alertas
        alert_mgr.check_cartera_vencida(761_274_180.0)
        alert_mgr.check_concentracion_clientes(25.3)

        assert len(alert_mgr.alerts) == 2

        # Limpiar alertas (0 horas = elimina todo)
        alert_mgr.clear_old_alerts(hours=0)

        assert len(alert_mgr.alerts) == 0

    def test_get_summary(self):
        """Test: Resumen de alertas"""
        alert_mgr = AlertManager()

        alert_mgr.check_cartera_vencida(761_274_180.0)  # CRÍTICA
        alert_mgr.check_concentracion_clientes(25.3)     # MEDIA

        summary = alert_mgr.get_summary()

        assert summary['total'] == 2
        assert summary['critical'] == 1
        assert summary['warning'] == 1


class TestAuditLogger:
    """Tests para AuditLogger"""

    def test_audit_table_creation(self):
        """Test: Tabla de auditoría se crea correctamente"""
        audit = AuditLogger()

        # Si no hay excepción, la tabla se creó
        assert audit is not None

    def test_log_workflow_event(self):
        """Test: Registrar evento de workflow"""
        audit = AuditLogger()

        result = audit.log_workflow_start(
            workflow_id="presupuesto",
            user_id="test_user",
            details={"monto": 5000000}
        )

        assert result == True

    def test_log_alert_event(self):
        """Test: Registrar alerta"""
        audit = AuditLogger()

        result = audit.log_alert(
            alert_type="cartera_vencida",
            kpi="cartera_vencida",
            current_value=761_274_180,
            threshold=100_000_000
        )

        assert result == True

    def test_log_error_event(self):
        """Test: Registrar error"""
        audit = AuditLogger()

        result = audit.log_error(
            error_type="workflow_execution_error",
            error_msg="Test error",
            context={"workflow_id": "presupuesto"}
        )

        assert result == True

    def test_get_audit_log(self):
        """Test: Obtener audit log"""
        audit = AuditLogger()

        # Registrar eventos
        audit.log_workflow_start("presupuesto")
        audit.log_workflow_start("venta")

        # Obtener logs
        logs = audit.get_audit_log(limit=100)

        assert isinstance(logs, list)
        assert len(logs) >= 2

    def test_audit_log_filters(self):
        """Test: Filtros en audit log"""
        audit = AuditLogger()

        # Registrar eventos
        audit.log_workflow_start("presupuesto", user_id="user1")
        audit.log_workflow_start("venta", user_id="user2")

        # Filtrar por usuario
        logs = audit.get_audit_log(user_id="user1")

        assert isinstance(logs, list)


class TestWorkflowExecutor:
    """Tests para WorkflowExecutor"""

    @pytest.mark.asyncio
    async def test_workflow_executor_init(self):
        """Test: Inicializar WorkflowExecutor"""
        agents = {
            "ceo_assistant": None,
            "cfo_assistant": None,
            "finance_agent": None,
        }

        executor = WorkflowExecutor(agents)

        assert executor is not None
        assert len(executor.agents) == 3

    @pytest.mark.asyncio
    async def test_execute_nonexistent_agent(self):
        """Test: Ejecutar agente que no existe"""
        executor = WorkflowExecutor({})

        result = await executor.execute_agent("nonexistent", "test query")

        assert "error" in result
        assert result["agent"] == "nonexistent"


# Suite de tests de integración
class TestIntegration:
    """Tests de integración del sistema completo"""

    def test_alert_manager_and_audit_together(self):
        """Test: AlertManager + AuditLogger integrados"""
        alert_mgr = AlertManager()
        audit = AuditLogger()

        # Generar alerta
        alert_mgr.check_cartera_vencida(761_274_180.0)

        # Registrar alerta
        audit.log_alert(
            alert_type="cartera_vencida",
            kpi="cartera_vencida",
            current_value=761_274_180,
            threshold=100_000_000
        )

        # Verificar que ambos funcionan
        assert len(alert_mgr.alerts) == 1
        logs = audit.get_audit_log(event_type="alert_triggered")
        assert isinstance(logs, list)

    def test_multiple_alerts(self):
        """Test: Múltiples alertas simultáneas"""
        alert_mgr = AlertManager()

        # Disparar 3 alertas
        alert_mgr.check_cartera_vencida(761_274_180.0)
        alert_mgr.check_concentracion_clientes(25.3)
        alert_mgr.check_proyectos_riesgo(4)

        summary = alert_mgr.get_summary()

        assert summary['total'] == 3
        assert summary['critical'] == 1
        assert summary['warning'] == 2


# Tests de performance
class TestPerformance:
    """Tests de performance y carga"""

    def test_alert_check_performance(self):
        """Test: Rendimiento de check de alertas"""
        alert_mgr = AlertManager()

        import time
        start = time.time()

        for i in range(1000):
            alert_mgr.check_cartera_vencida(761_274_180.0 + i)

        duration = time.time() - start

        # Debe procesar 1000 alertas en menos de 1 segundo
        assert duration < 1.0
        print(f"✅ 1000 alertas procesadas en {duration:.3f}s")

    def test_audit_log_performance(self):
        """Test: Rendimiento de registro de auditoría"""
        audit = AuditLogger()

        import time
        start = time.time()

        for i in range(100):
            audit.log_event(
                event_type=AuditEventType.WORKFLOW_START,
                action=f"Test workflow {i}",
                resource_id=f"workflow_{i}"
            )

        duration = time.time() - start

        # Debe registrar 100 eventos en menos de 5 segundos
        assert duration < 5.0
        print(f"✅ 100 eventos auditados en {duration:.3f}s")


if __name__ == "__main__":
    # Ejecutar con: pytest tests/test_workflows.py -v
    pytest.main([__file__, "-v", "--tb=short"])
