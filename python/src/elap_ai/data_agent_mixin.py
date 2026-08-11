"""Mixin para que agentes accedan a datos REALES desde PostgreSQL

Todos los agentes heredan de esto para obtener datos en tiempo real
sin necesidad de llamar a Ollama para respuestas estructuradas.
"""

import logging
import aiohttp
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class DataAgentMixin:
    """Mixin que proporciona acceso a datos REALES desde PostgreSQL"""

    def __init__(self):
        self.api_url = "http://localhost:5000/api/data/empresa"

    async def obtener_datos_reales(self, tabla: str = "employees", limite: int = 1000) -> List[Dict[str, Any]]:
        """Obtiene datos REALES desde PostgreSQL via API

        Args:
            tabla: employees, clients, products, transactions, evaluations, projects, pqrs
            limite: máximo de registros a retornar

        Returns:
            Lista de dictionaries con datos reales
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_url}?tabla={tabla}&limite={limite}") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        registros = data.get('datos', [])
                        logger.info(f"✅ Datos obtenidos de {tabla}: {len(registros)} registros")
                        return registros if isinstance(registros, list) else []
                    else:
                        logger.warning(f"⚠️ API retornó {resp.status}")
                        return []
        except Exception as e:
            logger.error(f"❌ Error obteniendo datos: {e}")
            return []

    async def obtener_resumen_empresa(self) -> Dict[str, Any]:
        """Obtiene resumen general de la empresa (estadísticas globales)"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_url}?tabla=resumen") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get('datos', {})
                    return {}
        except Exception as e:
            logger.error(f"Error obteniendo resumen: {e}")
            return {}

    # ============= FINANCE =============
    async def obtener_ingresos_por_canal(self) -> Dict[str, Any]:
        """Retorna ingresos totales y por canal de venta"""
        transacciones = await self.obtener_datos_reales("transactions")

        if not transacciones:
            return {"error": "No hay datos de transacciones"}

        canales = {}
        total = 0

        for trans in transacciones:
            canal = trans.get('canal', 'Desconocido')
            valor = float(trans.get('valor_total', 0))

            if canal not in canales:
                canales[canal] = {'total': 0, 'cantidad': 0}

            canales[canal]['total'] += valor
            canales[canal]['cantidad'] += 1
            total += valor

        # Ordenar por total descendente
        canales_ordenados = sorted(
            [(k, v['total']) for k, v in canales.items()],
            key=lambda x: x[1],
            reverse=True
        )

        return {
            "ingresos_totales": total,
            "canales_top_3": canales_ordenados[:3],
            "total_transacciones": len(transacciones)
        }

    # ============= SALES =============
    async def obtener_top_clientes(self, limite: int = 10) -> List[Dict[str, Any]]:
        """Retorna top N clientes por ventas"""
        clientes = await self.obtener_datos_reales("clients", 1000)

        if not clientes:
            return []

        # Ordenar por ventas_2025 descendente
        top = sorted(
            clientes,
            key=lambda x: x.get('ventas_2025', 0),
            reverse=True
        )[:limite]

        return [
            {
                'nombre': c.get('nombre'),
                'ciudad': c.get('ciudad'),
                'ventas_2024': c.get('ventas_2024'),
                'ventas_2025': c.get('ventas_2025'),
                'cartera_vencida': c.get('cartera_vencida_cop')
            }
            for c in top
        ]

    # ============= HR =============
    async def obtener_evaluaciones_por_depto(self) -> Dict[str, Any]:
        """Retorna evaluaciones y recomendaciones por departamento"""
        evaluaciones = await self.obtener_datos_reales("evaluations")
        empleados = await self.obtener_datos_reales("employees")

        if not evaluaciones or not empleados:
            return {"error": "Sin datos de evaluaciones o empleados"}

        # Mapear empleados por ID
        emp_map = {str(e.get('id_empleado')): e for e in empleados}

        # Agrupar por departamento
        por_depto = {}
        for ev in evaluaciones:
            depto = ev.get('departamento', 'Desconocido')

            if depto not in por_depto:
                por_depto[depto] = {
                    'puntaje_promedio': 0,
                    'cantidad': 0,
                    'ascensos': 0,
                    'capacitacion': 0
                }

            puntaje = int(ev.get('puntaje', 0))
            por_depto[depto]['puntaje_promedio'] += puntaje
            por_depto[depto]['cantidad'] += 1

            recom = ev.get('recomendacion', '').lower()
            if 'ascenso' in recom:
                por_depto[depto]['ascensos'] += 1
            elif 'capacitacion' in recom:
                por_depto[depto]['capacitacion'] += 1

        # Calcular promedios
        for depto in por_depto:
            cant = por_depto[depto]['cantidad']
            if cant > 0:
                por_depto[depto]['puntaje_promedio'] /= cant

        return por_depto

    # ============= CUSTOMER SERVICE =============
    async def obtener_pqrs_abiertos(self) -> Dict[str, Any]:
        """Retorna PQRS y quejas por estado y categoría"""
        pqrs = await self.obtener_datos_reales("pqrs")

        if not pqrs:
            return {"error": "Sin datos de PQRS"}

        por_estado = {}
        por_categoria = {}

        for p in pqrs:
            estado = p.get('estado', 'Desconocido')
            categoria = p.get('categoria', 'Desconocido')

            por_estado[estado] = por_estado.get(estado, 0) + 1
            por_categoria[categoria] = por_categoria.get(categoria, 0) + 1

        abiertos = por_estado.get('Abierto', 0)

        return {
            "total_pqrs": len(pqrs),
            "abiertos": abiertos,
            "por_estado": por_estado,
            "por_categoria": por_categoria,
            "categoria_mas_frecuente": max(por_categoria, key=por_categoria.get) if por_categoria else None
        }

    # ============= PROJECTS =============
    async def obtener_estado_proyectos(self) -> Dict[str, Any]:
        """Retorna estado y riesgos de proyectos"""
        proyectos = await self.obtener_datos_reales("projects")

        if not proyectos:
            return {"error": "Sin datos de proyectos"}

        en_riesgo = [p for p in proyectos if p.get('nivel_riesgo') in ['Crítico', 'Alto']]
        completados = [p for p in proyectos if p.get('estado') == 'Completado']

        return {
            "total_proyectos": len(proyectos),
            "en_riesgo": len(en_riesgo),
            "completados": len(completados),
            "proyectos_en_riesgo": [
                {
                    'nombre': p.get('nombre'),
                    'avance': p.get('avance_pct'),
                    'riesgo': p.get('nivel_riesgo')
                }
                for p in en_riesgo
            ]
        }
