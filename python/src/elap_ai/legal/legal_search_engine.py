"""Motor de búsqueda legal inteligente - SQLite + Web + APIs Oficiales

NOTA: Usando SQLite para desarrollo. En producción cambiar a Qdrant.
"""

import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import aiohttp
from pathlib import Path

from .official_apis import OfficialAPIs

logger = logging.getLogger(__name__)


class LegalSearchEngine:
    """Búsqueda inteligente de leyes colombianas con múltiples fuentes"""

    def __init__(self, db_path: str = "leyes_colombianas.db"):
        self.db_path = Path(db_path)
        self.official_apis = OfficialAPIs()
        self._init_database()

    def _init_database(self):
        """Inicializar base de datos SQLite"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Crear tabla de leyes si no existe
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS leyes (
                    id TEXT PRIMARY KEY,
                    texto TEXT NOT NULL,
                    fuente TEXT NOT NULL,
                    tema TEXT NOT NULL,
                    fecha_actualizacion TEXT NOT NULL,
                    url TEXT,
                    numero_resolucion TEXT,
                    edad_dias INTEGER DEFAULT 0
                )
            """)

            # Crear índices para búsqueda rápida
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_tema ON leyes(tema)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_fecha ON leyes(fecha_actualizacion)
            """)

            conn.commit()
            conn.close()

            logger.info(f"✅ Base de datos SQLite inicializada: {self.db_path}")

        except Exception as e:
            logger.error(f"Error inicializando base de datos: {e}")
            raise

    async def buscar_ley(
        self,
        query: str,
        tema: str = None,
        verificar_actualizacion: bool = True
    ) -> Dict[str, Any]:
        """
        Búsqueda inteligente de leyes con prioridad:
        1. APIs oficiales (más confiables)
        2. Qdrant local (<30 días)
        3. Web search a fuentes .gov.co
        """

        logger.info(f"🔍 Buscando: '{query}' | Tema: {tema}")

        # 1️⃣ Intentar APIs oficiales
        resultado_oficial = await self._buscar_en_apis(query, tema)
        if resultado_oficial and resultado_oficial.get("confianza", 0) > 0.9:
            logger.info(f"✅ Encontrado en APIs oficiales: {resultado_oficial['fuente']}")
            return resultado_oficial

        # 2️⃣ Buscar en SQLite local
        resultado_local = self._buscar_en_sqlite(query)
        if resultado_local:
            dias_antiguo = resultado_local.get("edad_dias", 0)

            if dias_antiguo < 30 and not verificar_actualizacion:
                logger.info(f"✅ Encontrado en SQLite (hace {dias_antiguo} días)")
                return resultado_local

            if dias_antiguo >= 30:
                logger.warning(
                    f"⚠️ Información local de hace {dias_antiguo} días, "
                    "verificando en web..."
                )

        # 3️⃣ Web search como backup
        resultado_web = await self._buscar_en_web(query)
        if resultado_web:
            logger.info(f"✅ Encontrado en web: {resultado_web['fuente']}")
            # Guardar en SQLite para próximas búsquedas
            await self._guardar_en_sqlite(resultado_web)
            return resultado_web

        # 4️⃣ Fallback
        logger.warning(f"❌ No se encontró información para: {query}")
        return {
            "error": "No se encontró información actualizada",
            "sugerencia": "Consultar canales oficiales:",
            "canales": [
                "Ministerio del Trabajo: https://www.mintrabajo.gov.co/",
                "DIAN: https://www.dian.gov.co/",
                "MinSalud: https://www.minsalud.gov.co/",
            ],
            "confianza": 0.0
        }

    async def _buscar_en_apis(self, query: str, tema: str = None) -> Optional[Dict]:
        """Buscar en APIs oficiales colombianas"""
        try:
            if not tema:
                tema = self._detectar_tema(query)

            if tema == "laboral":
                resultado = await self.official_apis.mintrabajo.get_codigo_sustantivo()
            elif tema == "salud":
                resultado = await self.official_apis.minsalud.get_afiliacion_eps()
            elif tema == "pension":
                resultado = await self.official_apis.superfinanciera.get_afiliacion_pension()
            elif tema == "fiscal":
                resultado = await self.official_apis.dian.get_descuentos_nomina()
            else:
                return None

            if resultado:
                resultado["confianza"] = 0.99
                return resultado
        except Exception as e:
            logger.error(f"Error en APIs oficiales: {e}")
        return None

    def _buscar_en_sqlite(self, query: str) -> Optional[Dict]:
        """Buscar en base de datos SQLite local"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query_lower = query.lower()

            # Búsqueda por coincidencia en texto o fuente
            cursor.execute("""
                SELECT * FROM leyes
                WHERE texto LIKE ? OR fuente LIKE ? OR tema LIKE ?
                ORDER BY fecha_actualizacion DESC
                LIMIT 1
            """, (f"%{query_lower}%", f"%{query_lower}%", f"%{query_lower}%"))

            row = cursor.fetchone()
            conn.close()

            if row:
                fecha_actual = datetime.fromisoformat(row["fecha_actualizacion"])
                dias_antiguo = (datetime.now() - fecha_actual).days

                return {
                    "texto": row["texto"],
                    "fuente": row["fuente"],
                    "fecha": row["fecha_actualizacion"],
                    "edad_dias": dias_antiguo,
                    "confianza": 0.95,
                    "oficial": True
                }
        except Exception as e:
            logger.error(f"Error buscando en SQLite: {e}")
        return None

    async def _buscar_en_web(self, query: str) -> Optional[Dict]:
        """Buscar en web filtrando por dominios .gov.co"""
        try:
            # Simulación de búsqueda (en producción: usar Google API o Brave Search)
            logger.info(f"🌐 Buscando en web: {query}")

            dominios_confiables = [
                "mintrabajo.gov.co",
                "dian.gov.co",
                "minsalud.gov.co",
                "superfinanciera.gov.co",
                "banrep.gov.co",
            ]

            # Aquí iría llamada a API de búsqueda (Google Custom Search, Brave, etc.)
            # Por ahora retornamos None para que use fallback
            logger.info("💡 Web search requiere configuración de API")
            return None

        except Exception as e:
            logger.error(f"Error en web search: {e}")
        return None

    async def _guardar_en_sqlite(self, ley: Dict[str, Any]):
        """Guardar ley en SQLite para búsquedas futuras"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            ley_id = str(hash(ley.get("fuente", "")))
            ahora = datetime.now().isoformat()

            cursor.execute("""
                INSERT OR REPLACE INTO leyes
                (id, texto, fuente, tema, fecha_actualizacion, url, numero_resolucion)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                ley_id,
                ley.get("texto", ""),
                ley.get("fuente", ""),
                ley.get("tema", "general"),
                ahora,
                ley.get("url", ""),
                ley.get("numero_resolucion")
            ))

            conn.commit()
            conn.close()

            logger.info(f"💾 Ley guardada en SQLite: {ley.get('fuente')}")
        except Exception as e:
            logger.error(f"Error guardando en SQLite: {e}")

    def _detectar_tema(self, query: str) -> str:
        """Detectar tema legal de la consulta"""
        query_lower = query.lower()

        temas = {
            "laboral": [
                "maternidad", "licencia", "embarazo", "salario", "sueldo",
                "nómina", "cesantía", "indemnización", "contrato",
                "empleado", "trabajador", "jornada", "horas extras"
            ],
            "salud": [
                "eps", "afiliación", "salud", "médico", "seguro",
                "medicina", "incapacidad"
            ],
            "pension": [
                "pensión", "afp", "jubilación", "fondo",
                "aporte", "contribución"
            ],
            "fiscal": [
                "impuesto", "retención", "descuento", "dian",
                "renta", "iva", "aporte"
            ]
        }

        for tema, keywords in temas.items():
            if any(kw in query_lower for kw in keywords):
                return tema

        return "laboral"  # Default

    async def sincronizar_todas_leyes(self):
        """Sincronizar TODAS las leyes desde fuentes oficiales"""
        logger.info("🔄 SINCRONIZACIÓN COMPLETA DE LEYES COLOMBIANAS")

        # Laborales
        leyes_laborales = await self.official_apis.get_all_leyes_laborales()
        logger.info(f"✅ {len(leyes_laborales)} leyes laborales sincronizadas")

        # Salud
        leyes_salud = await self.official_apis.get_all_leyes_salud()
        logger.info(f"✅ Leyes de salud sincronizadas")

        # Pensión
        leyes_pension = await self.official_apis.get_all_leyes_pension()
        logger.info(f"✅ Leyes de pensión sincronizadas")

        logger.info("✅ SINCRONIZACIÓN COMPLETADA")
        return {
            "laborales": leyes_laborales,
            "salud": leyes_salud,
            "pension": leyes_pension,
            "fecha": datetime.now().isoformat()
        }
