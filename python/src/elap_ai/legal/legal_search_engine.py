"""Motor de búsqueda legal inteligente - Qdrant + Web + APIs Oficiales"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
import aiohttp

from .official_apis import OfficialAPIs

logger = logging.getLogger(__name__)


class LegalSearchEngine:
    """Búsqueda inteligente de leyes colombianas con múltiples fuentes"""

    def __init__(self, qdrant_url: str = "http://localhost:6333"):
        self.qdrant = QdrantClient(qdrant_url)
        self.official_apis = OfficialAPIs()
        self.collection_name = "leyes_colombianas"
        self._init_collection()

    def _init_collection(self):
        """Inicializar colección en Qdrant si no existe"""
        try:
            self.qdrant.get_collection(self.collection_name)
            logger.info("✅ Colección 'leyes_colombianas' existe en Qdrant")
        except:
            logger.info("📝 Creando colección 'leyes_colombianas' en Qdrant...")
            # Crear con espacios vectoriales (768 dims para embeddings típicos)
            self.qdrant.recreate_collection(
                collection_name=self.collection_name,
                vectors_config={
                    "size": 768,
                    "distance": "Cosine"
                }
            )
            logger.info("✅ Colección creada")

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

        # 2️⃣ Buscar en Qdrant local
        resultado_local = self._buscar_en_qdrant(query)
        if resultado_local:
            dias_antiguo = resultado_local.get("edad_dias", 0)

            if dias_antiguo < 30 and not verificar_actualizacion:
                logger.info(f"✅ Encontrado en Qdrant (hace {dias_antiguo} días)")
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
            # Guardar en Qdrant para próximas búsquedas
            await self._guardar_en_qdrant(resultado_web)
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

    def _buscar_en_qdrant(self, query: str) -> Optional[Dict]:
        """Buscar en base vectorial local Qdrant"""
        try:
            # Aquí buscaríamos con embeddings, por ahora texto directo
            # En producción usarías: embedding = self.get_embedding(query)
            points = self.qdrant.scroll(self.collection_name, limit=100)

            if points[0]:  # Si hay documentos
                # Búsqueda simple por coincidencia (en producción: búsqueda vectorial)
                query_lower = query.lower()
                for point in points[0]:
                    payload = point.payload
                    if query_lower in payload.get("texto", "").lower():
                        dias_antiguo = (
                            datetime.now() - datetime.fromisoformat(
                                payload.get("fecha_actualizacion", datetime.now().isoformat())
                            )
                        ).days

                        return {
                            "texto": payload["texto"],
                            "fuente": payload.get("fuente", "Qdrant Local"),
                            "fecha": payload.get("fecha_actualizacion"),
                            "edad_dias": dias_antiguo,
                            "confianza": 0.95,
                            "oficial": True
                        }
        except Exception as e:
            logger.error(f"Error buscando en Qdrant: {e}")
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

    async def _guardar_en_qdrant(self, ley: Dict[str, Any]):
        """Guardar ley en Qdrant para búsquedas futuras"""
        try:
            point = PointStruct(
                id=hash(ley.get("fuente", "")),
                vector=[0.0] * 768,  # Vector dummy (en producción: embedding real)
                payload={
                    "texto": ley.get("texto", ""),
                    "fuente": ley.get("fuente", ""),
                    "tema": ley.get("tema", "general"),
                    "fecha_actualizacion": datetime.now().isoformat(),
                    "url": ley.get("url", ""),
                    "numero_resolucion": ley.get("numero_resolucion")
                }
            )
            self.qdrant.upsert(self.collection_name, [point])
            logger.info(f"💾 Ley guardada en Qdrant: {ley.get('fuente')}")
        except Exception as e:
            logger.error(f"Error guardando en Qdrant: {e}")

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
