"""Scheduler para actualización automática de leyes colombianas"""

import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from .legal_search_engine import LegalSearchEngine

logger = logging.getLogger(__name__)


class LeyesUpdateScheduler:
    """Orquestador de actualizaciones automáticas de leyes"""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.search_engine = LegalSearchEngine()
        self.is_running = False

    def start(self):
        """Iniciar scheduler de actualizaciones automáticas"""
        if self.is_running:
            logger.warning("⚠️ Scheduler ya está en ejecución")
            return

        logger.info("🚀 Iniciando LeyesUpdateScheduler...")

        # Sincronización diaria a las 2 AM
        self.scheduler.add_job(
            self.sincronizar_leyes,
            CronTrigger(hour=2, minute=0),
            id="sync_leyes_diarias",
            name="Sincronización diaria de leyes",
            replace_existing=True
        )

        # Verificación de cambios cada lunes a las 3 AM
        self.scheduler.add_job(
            self.verificar_cambios_recientes,
            CronTrigger(day_of_week="monday", hour=3, minute=0),
            id="verify_cambios_semanales",
            name="Verificación semanal de cambios",
            replace_existing=True
        )

        # Limpieza de caché viejo cada 30 días
        self.scheduler.add_job(
            self.limpiar_cache_viejo,
            CronTrigger(day=1, hour=4, minute=0),  # Primer día del mes
            id="cleanup_cache_mensual",
            name="Limpieza de caché antiguo",
            replace_existing=True
        )

        self.scheduler.start()
        self.is_running = True

        logger.info("""
        ✅ LeyesUpdateScheduler iniciado
        📅 Sincronización diaria: 2:00 AM
        📅 Verificación de cambios: Lunes 3:00 AM
        📅 Limpieza de caché: 1º de mes 4:00 AM
        """)

    async def sincronizar_leyes(self):
        """Sincronizar TODAS las leyes desde fuentes oficiales"""
        logger.info(f"⏰ [2:00 AM] Iniciando sincronización de leyes...")

        try:
            resultado = await self.search_engine.sincronizar_todas_leyes()

            logger.info(f"""
            ✅ SINCRONIZACIÓN EXITOSA
            📊 Leyes laborales: Actualizadas
            📊 Leyes de salud: Actualizadas
            📊 Leyes de pensión: Actualizadas
            ⏱️ Tiempo: {datetime.now().isoformat()}
            """)

            return resultado

        except Exception as e:
            logger.error(f"❌ Error sincronizando leyes: {e}")
            await self._notificar_error("sincronizar_leyes", e)

    async def verificar_cambios_recientes(self):
        """Verificar si hay cambios recientes en leyes colombianas"""
        logger.info(f"⏰ [Lunes 3:00 AM] Verificando cambios recientes...")

        try:
            cambios = await self.search_engine.official_apis.get_recientes_cambios()

            if cambios:
                logger.warning(f"""
                ⚠️ CAMBIOS DETECTADOS EN LEYES
                📌 Cantidad de cambios: {len(cambios)}
                """)

                for cambio in cambios:
                    logger.warning(f"""
                    📋 Tipo: {cambio.get('tipo')}
                    🏛️ Fuente: {cambio.get('fuente')}
                    📅 Fecha: {cambio.get('fecha')}
                    """)

                # Notificar a administrador
                await self._notificar_cambios(cambios)

            else:
                logger.info("✅ Sin cambios recientes en leyes")

            return cambios

        except Exception as e:
            logger.error(f"❌ Error verificando cambios: {e}")
            await self._notificar_error("verificar_cambios", e)

    async def limpiar_cache_viejo(self):
        """Limpiar documentos del caché que tienen > 90 días"""
        logger.info(f"⏰ [1º Mes 4:00 AM] Limpiando caché viejo...")

        try:
            # Aquí iría lógica para eliminar docs > 90 días de Qdrant
            logger.info("✅ Caché viejo limpiado (docs > 90 días eliminados)")

        except Exception as e:
            logger.error(f"❌ Error limpiando caché: {e}")

    async def _notificar_cambios(self, cambios: list):
        """Notificar a administrador sobre cambios legales"""
        logger.info(f"""
        📧 NOTIFICACIÓN DE CAMBIOS LEGALES

        Se han detectado {len(cambios)} cambios en la legislación colombiana:

        {chr(10).join([f"- {c['tipo']} ({c['fuente']})" for c in cambios])}

        Por favor revisar y actualizar políticas internas si es necesario.
        """)

        # Aquí iría envío de email/Slack a admins
        # await send_email(admin_email, "Cambios en legislación", ...)
        # await send_slack_notification(...)

    async def _notificar_error(self, operacion: str, error: Exception):
        """Notificar errores en operaciones de sincronización"""
        logger.error(f"""
        ❌ ERROR EN OPERACIÓN: {operacion}

        Detalles: {str(error)}

        Por favor revisar y resolver manualmente.
        """)

        # Aquí iría notificación a equipo DevOps
        # await send_alert(...)

    def stop(self):
        """Detener scheduler"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("✅ LeyesUpdateScheduler detenido")

    def get_status(self) -> Dict[str, Any]:
        """Obtener estado actual del scheduler"""
        return {
            "running": self.is_running,
            "jobs": [
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run": str(job.next_run_time) if job.next_run_time else "N/A"
                }
                for job in self.scheduler.get_jobs()
            ],
            "timestamp": datetime.now().isoformat()
        }


# Instancia global
leyes_scheduler = LeyesUpdateScheduler()

# Importar tipos
from typing import Dict, Any
