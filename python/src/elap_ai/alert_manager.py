"""Sistema de Alertas Inteligentes - Monitorea KPIs críticos"""

import logging
from typing import Dict, List, Any
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Niveles de severidad de alertas"""
    CRITICAL = "🚨 CRÍTICA"
    WARNING = "⚠️ MEDIA"
    INFO = "ℹ️ INFO"


class Alert:
    """Representa una alerta"""

    def __init__(self, level: AlertLevel, title: str, message: str, kpi: str, current_value: Any, threshold: Any):
        self.level = level
        self.title = title
        self.message = message
        self.kpi = kpi
        self.current_value = current_value
        self.threshold = threshold
        self.timestamp = datetime.now()
        self.id = f"{kpi}_{int(self.timestamp.timestamp())}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "level": self.level.value,
            "title": self.title,
            "message": self.message,
            "kpi": self.kpi,
            "current_value": self.current_value,
            "threshold": self.threshold,
            "timestamp": self.timestamp.isoformat()
        }


class AlertManager:
    """Gestor de alertas - Monitorea KPIs y genera alertas automáticas"""

    def __init__(self):
        self.alerts: List[Alert] = []
        self.rules = self._setup_rules()

    def _setup_rules(self) -> Dict[str, Dict[str, Any]]:
        """Define reglas de alerta para cada KPI"""
        return {
            "cartera_vencida": {
                "threshold": 100_000_000,  # $100M
                "level": AlertLevel.CRITICAL,
                "message_template": "Cartera vencida en ${current_value:,.0f} COP, exceede límite de ${threshold:,.0f}",
                "title": "Cartera Vencida Crítica"
            },
            "concentracion_clientes": {
                "threshold": 25,  # 25%
                "level": AlertLevel.WARNING,
                "message_template": "Concentración de ingresos en {current_value:.1f}% en un cliente, límite: {threshold}%",
                "title": "Concentración de Clientes Elevada"
            },
            "proyectos_riesgo": {
                "threshold": 2,
                "level": AlertLevel.WARNING,
                "message_template": "Hay {current_value} proyectos en riesgo, límite permitido: {threshold}",
                "title": "Proyectos en Riesgo"
            },
            "ingresos_variacion": {
                "threshold": 10,  # 10% bajada
                "level": AlertLevel.WARNING,
                "message_template": "Ingresos bajaron {current_value:.1f}% vs mes anterior, límite: {threshold}%",
                "title": "Variación de Ingresos"
            },
            "rotacion_empleados": {
                "threshold": 15,  # 15% anual
                "level": AlertLevel.WARNING,
                "message_template": "Rotación de empleados en {current_value:.1f}%, límite: {threshold}%",
                "title": "Rotación de Personal Elevada"
            },
            "margen_neto": {
                "threshold": 5,  # Menos del 5% es crítico
                "level": AlertLevel.CRITICAL,
                "message_template": "Margen neto bajo: {current_value:.1f}%, objetivo: >{threshold}%",
                "title": "Margen Neto Crítico"
            }
        }

    def check_cartera_vencida(self, cartera_vencida: float) -> None:
        """Verifica cartera vencida contra umbral"""
        rule = self.rules["cartera_vencida"]
        if cartera_vencida > rule["threshold"]:
            alert = Alert(
                level=rule["level"],
                title=rule["title"],
                message=rule["message_template"].format(
                    current_value=cartera_vencida,
                    threshold=rule["threshold"]
                ),
                kpi="cartera_vencida",
                current_value=cartera_vencida,
                threshold=rule["threshold"]
            )
            self.alerts.append(alert)
            logger.warning(f"🚨 ALERTA: {alert.title} - ${cartera_vencida:,.0f}")

    def check_concentracion_clientes(self, concentracion_pct: float) -> None:
        """Verifica concentración de ingresos en clientes"""
        rule = self.rules["concentracion_clientes"]
        if concentracion_pct > rule["threshold"]:
            alert = Alert(
                level=rule["level"],
                title=rule["title"],
                message=rule["message_template"].format(
                    current_value=concentracion_pct,
                    threshold=rule["threshold"]
                ),
                kpi="concentracion_clientes",
                current_value=concentracion_pct,
                threshold=rule["threshold"]
            )
            self.alerts.append(alert)
            logger.warning(f"⚠️ ALERTA: {alert.title} - {concentracion_pct:.1f}%")

    def check_proyectos_riesgo(self, proyectos_riesgo: int) -> None:
        """Verifica cantidad de proyectos en riesgo"""
        rule = self.rules["proyectos_riesgo"]
        if proyectos_riesgo > rule["threshold"]:
            alert = Alert(
                level=rule["level"],
                title=rule["title"],
                message=rule["message_template"].format(
                    current_value=proyectos_riesgo,
                    threshold=rule["threshold"]
                ),
                kpi="proyectos_riesgo",
                current_value=proyectos_riesgo,
                threshold=rule["threshold"]
            )
            self.alerts.append(alert)
            logger.warning(f"⚠️ ALERTA: {alert.title} - {proyectos_riesgo} proyectos")

    def check_ingresos_variacion(self, variacion_pct: float) -> None:
        """Verifica variación de ingresos mes a mes"""
        rule = self.rules["ingresos_variacion"]
        if variacion_pct < -rule["threshold"]:  # Bajada más del 10%
            alert = Alert(
                level=rule["level"],
                title=rule["title"],
                message=rule["message_template"].format(
                    current_value=variacion_pct,
                    threshold=rule["threshold"]
                ),
                kpi="ingresos_variacion",
                current_value=variacion_pct,
                threshold=rule["threshold"]
            )
            self.alerts.append(alert)
            logger.warning(f"⚠️ ALERTA: {alert.title} - {variacion_pct:.1f}%")

    def check_margen_neto(self, margen_neto: float) -> None:
        """Verifica margen neto de la empresa"""
        rule = self.rules["margen_neto"]
        if margen_neto < rule["threshold"]:
            alert = Alert(
                level=rule["level"],
                title=rule["title"],
                message=rule["message_template"].format(
                    current_value=margen_neto,
                    threshold=rule["threshold"]
                ),
                kpi="margen_neto",
                current_value=margen_neto,
                threshold=rule["threshold"]
            )
            self.alerts.append(alert)
            logger.warning(f"🚨 ALERTA: {alert.title} - {margen_neto:.1f}%")

    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Retorna todas las alertas activas"""
        return [alert.to_dict() for alert in self.alerts]

    def get_alerts_by_level(self, level: AlertLevel) -> List[Dict[str, Any]]:
        """Retorna alertas por nivel de severidad"""
        filtered = [a for a in self.alerts if a.level == level]
        return [alert.to_dict() for alert in filtered]

    def clear_old_alerts(self, hours: int = 24) -> None:
        """Limpia alertas más antiguas que N horas"""
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(hours=hours)
        self.alerts = [a for a in self.alerts if a.timestamp > cutoff]

    def get_summary(self) -> Dict[str, Any]:
        """Retorna resumen de alertas"""
        critical = len([a for a in self.alerts if a.level == AlertLevel.CRITICAL])
        warning = len([a for a in self.alerts if a.level == AlertLevel.WARNING])
        info = len([a for a in self.alerts if a.level == AlertLevel.INFO])

        return {
            "total": len(self.alerts),
            "critical": critical,
            "warning": warning,
            "info": info,
            "alerts": self.get_active_alerts()
        }
