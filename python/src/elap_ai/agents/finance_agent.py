"""Agente de Finanzas - Generación de reportes y facturas"""

import logging
from typing import Dict, Any, List
from datetime import datetime
import uuid

from elap_ai.agent_runtime.agent import Agent, AgentState
from elap_ai.document_engine import DocumentEngine

logger = logging.getLogger(__name__)


class FinanceAgent(Agent):
    """Agente especializado en Finanzas

    Genera reportes financieros, facturas, presupuestos y análisis.
    Integrado con Document Engine para documentos profesionales.
    """

    def __init__(self, name: str = "Finance Assistant", role: str = "Finance", theme: str = "andina_foods"):
        """Inicializa agente de Finanzas"""
        # Crear AgentState
        state = AgentState(
            id=str(uuid.uuid4()),
            name=name,
            role=role,
            objective="Generate financial documents: reports, invoices, budgets, analysis"
        )
        super().__init__(state=state)
        self.theme = theme
        self.document_engine = DocumentEngine(theme=theme, language="es")
        logger.info(f"Finance Agent initialized with theme: {theme}")

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

        # Verificar si tiene datos de factura
        has_invoice_data = all(keyword in query for keyword in ["Factura:", "Cliente:", "Items:"])

        # Si tiene datos, GENERAR la factura
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

        # Si NO tiene datos pero pide factura, solicitar datos
        elif any(word in query_lower for word in ["factura", "invoice", "boleta", "comprobante"]):
            return {
                "intent": "generate_invoice",
                "message": """💰 *Asistente de Finanzas* aquí.

Veo que necesitas generar una **factura**.

Para crearla necesito:
• Número de factura
• Nombre del cliente
• Fecha de emisión
• Fecha de vencimiento
• Items (descripción, precio, cantidad)
• Condiciones de pago

¿Proporcionas los detalles para generar la factura?""",
                "required_fields": ["numero", "cliente", "items", "fecha"]
            }

        elif any(word in query_lower for word in ["reporte", "report", "análisis", "analysis", "estado"]):
            return {
                "intent": "generate_report",
                "message": """💰 *Asistente de Finanzas* aquí.

Veo que necesitas un **reporte financiero**.

Para generarlo necesito:
• Título del reporte
• Período (trimestre, año, etc)
• Resumen ejecutivo
• Métricas clave (ventas, utilidad, margen)
• Análisis detallado
• Conclusiones

¿Cuál es el período del reporte y qué métricas quieres incluir?""",
                "required_fields": ["titulo", "periodo", "metricas"]
            }

        else:
            # GENÉRICO: Usar Ollama con system prompt de Finanza
            try:
                from ..ollama_client import OllamaClient
                from ..system_prompts import get_system_prompt

                ollama = OllamaClient()
                system_prompt = get_system_prompt("finance_agent")

                prompt_ollama = f"""{system_prompt}

Pregunta del usuario: {query}

Responde de manera profesional, analítica y con datos cuando sea posible."""

                logger.info("💰 Llamando a Ollama para respuesta general de Finanzas...")
                respuesta = await ollama.generar("glm4:9b", prompt_ollama)

                return {
                    "intent": "general_query",
                    "message": f"💰 *Asistente de Finanzas*\n\n{respuesta}"
                }
            except Exception as e:
                logger.error(f"Ollama error en Finance: {e}")
                return {
                    "intent": "general_query",
                    "message": """💰 *Asistente de Finanzas* a tu servicio.

Soy especialista en documentación financiera. Puedo ayudarte con:

🧾 **Facturas** - Facturas, notas crédito/débito
📊 **Reportes** - Ingresos, flujo de caja, análisis
💡 **Análisis** - Presupuestos, proyecciones, rentabilidad

¿Qué necesitas? Cuéntame los detalles."""
                }
