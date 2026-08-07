"""Research Agent - Agente especializado en búsqueda de información

Utiliza la herramienta WebSearchTool para investigar temas y proporcionar
información detallada a partir de búsquedas simuladas.
"""

import asyncio
import logging
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Resultado de una búsqueda"""
    titulo: str
    url: str
    extracto: str
    relevancia: float


@dataclass
class ResearchOutput:
    """Salida de investigación"""
    tema: str
    resultados: list
    resumen: str
    fuentes: int


class ResearchAgent:
    """Agente especializado en investigación y búsqueda de información"""

    def __init__(self, nombre: str = "Research Agent"):
        self.nombre = nombre
        self.historial_busquedas = []
        logger.info(f"ResearchAgent '{nombre}' inicializado")

    async def investigar(self, tema: str, profundidad: str = "basica") -> ResearchOutput:
        """
        Investiga un tema y retorna información estructurada

        Args:
            tema: Tema a investigar
            profundidad: "basica", "intermedia" o "profunda"

        Returns:
            ResearchOutput con resultados de investigación
        """
        logger.info(f"Iniciando investigación sobre: {tema}")

        # Validar entrada
        if not tema or len(tema.strip()) == 0:
            raise ValueError("El tema no puede estar vacío")

        # Simular búsqueda (en producción, llamar a WebSearchTool)
        resultados = await self._buscar(tema, profundidad)

        # Generar resumen
        resumen = self._generar_resumen(resultados, profundidad)

        # Registrar búsqueda
        self.historial_busquedas.append({
            "tema": tema,
            "profundidad": profundidad,
            "cantidad_resultados": len(resultados),
        })

        return ResearchOutput(
            tema=tema,
            resultados=resultados,
            resumen=resumen,
            fuentes=len(resultados),
        )

    async def _buscar(self, tema: str, profundidad: str) -> list:
        """Realiza búsqueda simulada"""
        await asyncio.sleep(0.1)  # Simular latencia

        resultados = [
            SearchResult(
                titulo=f"Información completa sobre {tema}",
                url="https://ejemplo.com/tema-1",
                extracto=f"Este documento proporciona una visión general de {tema}.",
                relevancia=0.95,
            ),
            SearchResult(
                titulo=f"Análisis profundo: {tema}",
                url="https://ejemplo.com/tema-2",
                extracto=f"Análisis detallado de los aspectos clave de {tema}.",
                relevancia=0.87,
            ),
        ]

        # Agregar resultados adicionales según profundidad
        if profundidad in ["intermedia", "profunda"]:
            resultados.append(
                SearchResult(
                    titulo=f"Casos de uso de {tema}",
                    url="https://ejemplo.com/tema-3",
                    extracto=f"Aplicaciones prácticas de {tema} en el mundo real.",
                    relevancia=0.78,
                )
            )

        if profundidad == "profunda":
            resultados.extend([
                SearchResult(
                    titulo=f"Historia y evolución de {tema}",
                    url="https://ejemplo.com/tema-4",
                    extracto=f"Cómo ha evolucionado {tema} a lo largo del tiempo.",
                    relevancia=0.72,
                ),
                SearchResult(
                    titulo=f"Tendencias futuras en {tema}",
                    url="https://ejemplo.com/tema-5",
                    extracto=f"Predicciones sobre el futuro de {tema}.",
                    relevancia=0.68,
                ),
            ])

        return resultados

    def _generar_resumen(self, resultados: list, profundidad: str) -> str:
        """Genera un resumen de los resultados"""
        cantidad = len(resultados)

        resumen = f"Se encontraron {cantidad} fuentes sobre el tema. "

        if profundidad == "basica":
            resumen += "Búsqueda rápida con información general."
        elif profundidad == "intermedia":
            resumen += "Búsqueda intermedia con análisis de casos de uso."
        else:
            resumen += "Búsqueda profunda incluyendo historia y tendencias futuras."

        return resumen

    def get_historial(self) -> list:
        """Retorna el historial de búsquedas realizadas"""
        return self.historial_busquedas

    def limpiar_historial(self) -> None:
        """Limpia el historial de búsquedas"""
        self.historial_busquedas = []
        logger.info("Historial de búsquedas limpiado")


# Funciones helper para integración con LangGraph
async def buscar_informacion(tema: str, profundidad: str = "basica") -> dict:
    """Wrapper para usar ResearchAgent en LangGraph"""
    agent = ResearchAgent("Research Agent")
    resultado = await agent.investigar(tema, profundidad)

    return {
        "tema": resultado.tema,
        "resultados": [
            {
                "titulo": r.titulo,
                "url": r.url,
                "extracto": r.extracto,
                "relevancia": r.relevancia,
            }
            for r in resultado.resultados
        ],
        "resumen": resultado.resumen,
        "fuentes": resultado.fuentes,
    }
