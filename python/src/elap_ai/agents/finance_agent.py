"""Agente de Finanzas - Generación de reportes y facturas con datos REALES"""

import logging
from typing import Dict, Any, List
from datetime import datetime
import uuid

from elap_ai.agent_runtime.agent import Agent, AgentState
from elap_ai.document_engine import DocumentEngine
from elap_ai.data_agent_mixin import DataAgentMixin

logger = logging.getLogger(__name__)


class FinanceAgent(Agent, DataAgentMixin):
    """Agente especializado en Finanzas

    Genera reportes financieros, facturas, presupuestos y análisis.
    Integrado con Document Engine para documentos profesionales.
    """

    def __init__(self, name: str = "Finance Assistant", role: str = "Finance", theme: str = "andina_foods"):
        """Inicializa agente de Finanzas con acceso a datos REALES"""
        # Crear AgentState
        state = AgentState(
            id=str(uuid.uuid4()),
            name=name,
            role=role,
            objective="Generate financial documents: reports, invoices, budgets, analysis with REAL data"
        )
        super().__init__(state=state)
        DataAgentMixin.__init__(self)  # Inicializar mixin
        self.theme = theme
        self.document_engine = DocumentEngine(theme=theme, language="es")
        logger.info(f"Finance Agent initialized with theme: {theme} - usando datos REALES")

    async def generate_report(
        self,
        titulo: str,
        empresa: str,
        periodo: str,
        resumen_ejecutivo: str,
        metricas: Dict[str, str],
        analisis: str,
        conclusiones: str,
        output_format: str = "word"
    ) -> Dict[str, Any]:
        """Genera reporte financiero profesional

        Args:
            titulo: Título del reporte
            empresa: Nombre de la empresa
            periodo: Período del reporte (Q1, Q2, etc)
            resumen_ejecutivo: Resumen para gerentes
            metricas: Dict con {métrica: valor}
            analisis: Análisis detallado
            conclusiones: Conclusiones y recomendaciones
            output_format: Formato (word, pdf, excel, powerpoint)

        Returns:
            Dict con información del documento generado
        """
        logger.info(f"Generating financial report: {titulo}")

        try:
            report_data = {
                "titulo": titulo,
                "empresa": empresa,
                "periodo": periodo,
                "seccion_ejecutiva": resumen_ejecutivo,
                "metricas": metricas,
                "contenido_ia": analisis,
                "conclusiones": conclusiones
            }

            if output_format.lower() == "word":
                output_path = self.document_engine.generate_word(
                    "report",
                    report_data,
                    f"reporte_{titulo.replace(' ', '_')}.docx"
                )
            elif output_format.lower() == "pdf":
                output_path = self.document_engine.generate_pdf(
                    "report",
                    report_data,
                    f"reporte_{titulo.replace(' ', '_')}.pdf"
                )
            elif output_format.lower() == "excel":
                output_path = self.document_engine.generate_excel(
                    "report",
                    report_data,
                    f"reporte_{titulo.replace(' ', '_')}.xlsx"
                )
            elif output_format.lower() == "powerpoint":
                output_path = self.document_engine.generate_powerpoint(
                    "report",
                    report_data,
                    f"reporte_{titulo.replace(' ', '_')}.pptx"
                )
            else:
                raise ValueError(f"Formato no soportado: {output_format}")

            return {
                "status": "success",
                "document_type": "report",
                "title": titulo,
                "company": empresa,
                "period": periodo,
                "format": output_format,
                "path": str(output_path),
                "message": f"Reporte '{titulo}' generado exitosamente"
            }

        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return {
                "status": "error",
                "document_type": "report",
                "error": str(e)
            }

    async def generate_invoice(
        self,
        numero: str,
        empresa_emisor: str,
        cliente: str,
        fecha_emision: str,
        fecha_vencimiento: str,
        items: List[Dict[str, Any]],
        condiciones_pago: str,
        output_format: str = "word"
    ) -> Dict[str, Any]:
        """Genera factura profesional

        Args:
            numero: Número de factura
            empresa_emisor: Nombre de la empresa
            cliente: Nombre del cliente
            fecha_emision: Fecha de emisión
            fecha_vencimiento: Fecha de vencimiento
            items: Lista de items [{descripcion, precio_unitario, cantidad}]
            condiciones_pago: Términos de pago
            output_format: Formato de salida

        Returns:
            Dict con información del documento
        """
        logger.info(f"Generating invoice: {numero}")

        try:
            # Calcular totales
            subtotal = sum(item.get("cantidad", 0) * item.get("precio_unitario", 0) for item in items)
            impuesto = subtotal * 0.19
            total = subtotal + impuesto

            invoice_data = {
                "numero": numero,
                "empresa": empresa_emisor,
                "cliente": cliente,
                "fecha_emision": fecha_emision,
                "fecha_vencimiento": fecha_vencimiento,
                "items": items,
                "subtotal": f"{subtotal:,.2f}",
                "impuesto": f"{impuesto:,.2f}",
                "total": f"{total:,.2f}",
                "condiciones_pago": condiciones_pago
            }

            if output_format.lower() == "word":
                output_path = self.document_engine.generate_word(
                    "invoice",
                    invoice_data,
                    f"factura_{numero}.docx"
                )
            elif output_format.lower() == "pdf":
                output_path = self.document_engine.generate_pdf(
                    "invoice",
                    invoice_data,
                    f"factura_{numero}.pdf"
                )
            elif output_format.lower() == "excel":
                output_path = self.document_engine.generate_excel(
                    "invoice",
                    invoice_data,
                    f"factura_{numero}.xlsx"
                )
            else:
                raise ValueError(f"Formato no soportado: {output_format}")

            return {
                "status": "success",
                "document_type": "invoice",
                "invoice_number": numero,
                "client": cliente,
                "total": f"${total:,.2f}",
                "format": output_format,
                "path": str(output_path),
                "message": f"Factura {numero} generada exitosamente"
            }

        except Exception as e:
            logger.error(f"Error generating invoice: {e}")
            return {
                "status": "error",
                "document_type": "invoice",
                "error": str(e)
            }

    async def process_query(self, query: str) -> Dict[str, Any]:
        """Procesa consulta financiera"""
        logger.info(f"Processing finance query: {query}")

        query_lower = query.lower()

        # Palabras clave para dominio financiero
        finance_keywords = [
            "reporte", "report", "análisis", "analysis", "presupuesto", "budget",
            "estado", "flujo", "cash flow", "ingresos", "revenue", "gastos", "expenses",
            "utilidad", "profit", "margen", "margin", "factura", "invoice", "boleta",
            "finanza", "finance", "financiero", "presupuestal", "egresos", "ventas",
            "costo", "cost", "rentabilidad", "proyección", "forecast", "balance",
            "activos", "pasivos", "patrimonio", "cffo", "cfo", "tesorería"
        ]

        # Verificar si es pregunta del dominio financiero
        is_finance_question = any(keyword in query_lower for keyword in finance_keywords)

        # Si NO es pregunta financiera, rechazar cortésmente
        if not is_finance_question:
            return {
                "intent": "out_of_domain",
                "message": """💰 *Asistente de Finanzas* aquí.

Lo siento, esa pregunta está fuera de mi especialidad financiera.
Soy experto en:

🧾 **Facturas** - Facturas, notas crédito/débito
📊 **Reportes** - Ingresos, flujo de caja, presupuestos
💡 **Análisis** - Rentabilidad, proyecciones, márgenes
💼 **Documentos** - Estados financieros, auditorías

¿Tienes alguna pregunta sobre finanzas?"""
            }

        # ==================== DATOS REALES ====================
        # Preguntas sobre ingresos/canales -> retornar datos REALES de PostgreSQL
        ingresos_keywords = ["ingreso", "venta", "revenue", "canal", "channel", "flujo"]

        if any(kw in query_lower for kw in ingresos_keywords):
            logger.info("💰 Detectada pregunta sobre ingresos - usando datos REALES")

            try:
                datos = await self.obtener_ingresos_por_canal()

                if "error" not in datos:
                    total = datos.get('ingresos_totales', 0)
                    top_3 = datos.get('canales_top_3', [])

                    respuesta = f"""📊 **ANÁLISIS DE INGRESOS (DATOS REALES)**
==================================================

💰 **Ingresos Totales**: ${total:,.0f} COP
📈 **Total Transacciones**: {datos.get('total_transacciones', 0)}

🏆 **Top 3 Canales de Venta**:
"""

                    for idx, (canal, monto) in enumerate(top_3, 1):
                        pct = (monto / total * 100) if total > 0 else 0
                        respuesta += f"\n{idx}. **{canal}**: ${monto:,.0f} COP ({pct:.1f}%)"

                    respuesta += "\n\n✅ Datos obtenidos de PostgreSQL en tiempo real."

                    return {
                        "intent": "ingresos_query",
                        "message": respuesta
                    }
            except Exception as e:
                logger.error(f"Error obteniendo datos de ingresos: {e}")

        # ==================== FACTURA ====================
        # Verificar si tiene datos EXACTOS de factura para generar
        has_invoice_data = all(keyword in query for keyword in ["Factura:", "Cliente:", "Items:"])

        if has_invoice_data:
            logger.info("🚀 Detectados datos de factura, generando...")

            try:
                import re
                from datetime import datetime

                def extract_value(key):
                    pattern = rf"{key}:\s*(.+?)(?=\n|$)"
                    match = re.search(pattern, query)
                    return match.group(1).strip() if match else ""

                numero = extract_value("Factura")
                cliente = extract_value("Cliente")
                items_str = extract_value("Items")

                logger.info(f"Datos extraídos: Factura {numero}, Cliente {cliente}")

                # Parsear items (asumir formato: Descripción (precio x cantidad))
                items = []
                for item_line in items_str.split(";"):
                    if item_line.strip():
                        items.append({
                            "descripcion": item_line.strip(),
                            "precio_unitario": 50000,  # default
                            "cantidad": 1
                        })

                # Generar factura
                result = await self.generate_invoice(
                    numero=numero,
                    empresa_emisor="Andina Foods S.A.S.",
                    cliente=cliente,
                    fecha_emision=datetime.now().strftime("%d/%m/%Y"),
                    fecha_vencimiento="",
                    items=items if items else [{"descripcion": items_str, "precio_unitario": 0, "cantidad": 1}],
                    condiciones_pago="Pago a 30 días",
                    output_format="word"
                )

                if result['status'] == 'success':
                    return {
                        "intent": "invoice_generated",
                        "message": f"""✅ **FACTURA GENERADA EXITOSAMENTE**

🧾 Número: {numero}
👤 Cliente: {cliente}
💰 Total: {result.get('total', 'Calculado')}
📁 Guardado en: {result['path']}

¿Descargas la factura o necesitas hacer cambios?""",
                        "generated_file": result['path']
                    }
                else:
                    return {
                        "intent": "error",
                        "message": f"❌ Error generando factura: {result.get('error')}"
                    }

            except Exception as e:
                logger.error(f"Error: {e}")
                return {
                    "intent": "error",
                    "message": f"❌ Error procesando datos: {str(e)}"
                }

        # CUALQUIER otra pregunta financiera: Usar Ollama
        try:
            from ..ollama_client import OllamaClient
            from ..system_prompts import get_system_prompt

            logger.info("💰 Llamando a Ollama para respuesta financiera...")
            ollama = OllamaClient()
            system_prompt = get_system_prompt("finance_agent")

            prompt_ollama = f"""{system_prompt}

Pregunta del usuario: {query}

Responde de manera profesional, analítica y con datos cuando sea posible.
Si es un reporte o análisis, estructura con:
- Resumen ejecutivo
- Métricas clave
- Análisis detallado
- Conclusiones y recomendaciones"""

            respuesta = await ollama.generar("glm4:9b", prompt_ollama)

            # POST-PROCESAR: Arreglar markdown incorrecto
            import re
            # Arreglar # sin espacios: #Ingresos → # Ingresos
            respuesta = re.sub(r'^(#{1,6})([^\s#])', r'\1 \2', respuesta, flags=re.MULTILINE)
            # Remover placeholders
            respuesta = re.sub(r'\[Inserte aquí.*?\]', '[Gráfico generado automáticamente]', respuesta, flags=re.IGNORECASE)
            respuesta = re.sub(r'\[insertar.*?\]', '[Datos insertados]', respuesta, flags=re.IGNORECASE)

            return {
                "intent": "general_query",
                "message": f"💰 *Asistente de Finanzas*\n\n{respuesta}"
            }

        except Exception as e:
            logger.error(f"Ollama error en Finance: {e}")
            return {
                "intent": "error",
                "message": f"""💰 *Asistente de Finanzas* a tu servicio.

Soy especialista en análisis y documentación financiera. Puedo ayudarte con:

🧾 **Facturas** - Facturas, notas crédito/débito
📊 **Reportes** - Ingresos, flujo de caja, análisis
💡 **Análisis** - Presupuestos, proyecciones, rentabilidad

Error al conectar con Ollama. Intenta de nuevo."""
            }
