"""Document Manager Agent - Nivel Documentación con datos REALES"""

import logging
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path
import json

from elap_ai.data_agent_mixin import DataAgentMixin

logger = logging.getLogger(__name__)


class DocumentManagerAgent(DataAgentMixin):
    """Agente Gestor Documental - Administra documentos y archivos con datos REALES"""

    def __init__(self, theme: str = "andina_foods"):
        super().__init__()
        self.theme = theme
        self.document_index = {}  # En memoria: {doc_id: metadata}
        self.index_file = Path("/tmp/document_index.json")
        self._load_index()
        logger.info(f"DocumentManagerAgent initialized with theme: {theme} - usando datos REALES")

    def _load_index(self):
        """Cargar índice de documentos desde archivo"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r') as f:
                    self.document_index = json.load(f)
                logger.info(f"✅ Índice cargado: {len(self.document_index)} documentos")
            except Exception as e:
                logger.error(f"Error cargando índice: {e}")
                self.document_index = {}

    def _save_index(self):
        """Guardar índice de documentos"""
        try:
            with open(self.index_file, 'w') as f:
                json.dump(self.document_index, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error guardando índice: {e}")

    async def register_document(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Registrar un documento generado por otro agente

        Args:
            document_data: {
                'file_path': str,
                'doc_type': 'contract'|'invoice'|'report',
                'agent_name': str,
                'entity_id': str (empleado_id, cliente_id, etc),
                'entity_name': str,
                'metadata': dict (cualquier dato adicional)
            }

        Returns:
            Dict con resultado del registro
        """
        try:
            doc_id = f"{document_data['doc_type']}_{document_data['entity_id']}_{datetime.now().timestamp()}"

            registro = {
                'doc_id': doc_id,
                'file_path': document_data.get('file_path'),
                'doc_type': document_data.get('doc_type'),
                'agent_name': document_data.get('agent_name'),
                'entity_id': document_data.get('entity_id'),
                'entity_name': document_data.get('entity_name'),
                'created_at': datetime.now().isoformat(),
                'metadata': document_data.get('metadata', {})
            }

            self.document_index[doc_id] = registro
            self._save_index()

            logger.info(f"📄 Documento registrado: {doc_id} ({document_data['doc_type']}) by {document_data['agent_name']}")

            return {
                'status': 'success',
                'doc_id': doc_id,
                'message': f"Documento {document_data['doc_type']} registrado exitosamente"
            }
        except Exception as e:
            logger.error(f"Error registrando documento: {e}")
            return {'status': 'error', 'message': str(e)}

    async def get_documents(self, doc_type: str = None, agent_name: str = None, entity_id: str = None) -> List[Dict[str, Any]]:
        """Recuperar documentos por filtros

        Args:
            doc_type: 'contract', 'invoice', 'report', etc
            agent_name: nombre del agente que generó
            entity_id: ID de la entidad (empleado, cliente, etc)

        Returns:
            Lista de documentos que coinciden con los filtros
        """
        resultados = []

        for doc_id, doc in self.document_index.items():
            if doc_type and doc.get('doc_type') != doc_type:
                continue
            if agent_name and doc.get('agent_name') != agent_name:
                continue
            if entity_id and doc.get('entity_id') != entity_id:
                continue

            resultados.append(doc)

        logger.info(f"🔍 Búsqueda: {len(resultados)} documentos encontrados")
        return sorted(resultados, key=lambda x: x.get('created_at'), reverse=True)

    async def process_query(self, query: str) -> Dict[str, Any]:
        """Procesar consulta de gestión documental"""
        logger.info(f"Processing document management query: {query[:50]}...")

        query_lower = query.lower()

        # ==================== BÚSQUEDA EN ÍNDICE ====================
        # Palabras clave para buscar documentos registrados
        busqueda_keywords = ["contrato", "factura", "reporte", "generado", "creado", "archivo"]

        if any(kw in query_lower for kw in busqueda_keywords):
            logger.info("🔍 Detectada búsqueda de documentos - consultando índice")

            try:
                # Detectar tipo de documento
                doc_type = None
                if "contrato" in query_lower:
                    doc_type = "contract"
                elif "factura" in query_lower:
                    doc_type = "invoice"
                elif "reporte" in query_lower:
                    doc_type = "report"

                documentos = await self.get_documents(doc_type=doc_type)

                if documentos:
                    respuesta = f"""📄 **DOCUMENTOS REGISTRADOS**
==================================================================

📊 **RESUMEN**
  • Total documentos: {len(documentos)}
  • Tipo: {doc_type or 'Todos'}

📋 **DOCUMENTOS RECIENTES**

"""
                    for idx, doc in enumerate(documentos[:10], 1):
                        fecha = doc.get('created_at', 'N/A')[:10]
                        tipo = doc.get('doc_type', 'N/A')
                        entidad = doc.get('entity_name', 'Desconocido')
                        agente = doc.get('agent_name', 'N/A')

                        respuesta += f"{idx}. [{fecha}] {tipo.upper()} - {entidad}\n"
                        respuesta += f"   Generado por: {agente}\n"
                        respuesta += f"   Ruta: {doc.get('file_path', 'N/A')}\n\n"

                    respuesta += "✅ Documentos desde índice en tiempo real."

                    return {
                        "intent": "documento_query",
                        "message": respuesta
                    }
                else:
                    return {
                        "intent": "documento_query",
                        "message": f"📄 No hay documentos registrados de tipo {doc_type or 'especificado'}."
                    }
            except Exception as e:
                logger.error(f"Error buscando documentos: {e}")

        # ==================== DATOS REALES ====================
        # Palabras clave para documentos generales
        documento_keywords = ["documento", "archivo", "transacción", "comprobante", "registro"]

        if any(kw in query_lower for kw in documento_keywords):
            logger.info("📄 Detectada pregunta sobre documentos - usando datos REALES")

            try:
                transacciones = await self.obtener_datos_reales("transactions", limite=100)

                if transacciones:
                    respuesta = f"""📄 **GESTIÓN DE DOCUMENTOS Y REGISTROS (DATOS REALES)**
==================================================================

📊 **RESUMEN DE TRANSACCIONES DOCUMENTADAS**
  • Total de Transacciones: {len(transacciones)}
  • Documentos Registrados: {len(transacciones)}

📋 **ÚLTIMAS TRANSACCIONES**

"""
                    # Mostrar últimas 10 transacciones
                    for idx, trans in enumerate(transacciones[-10:], 1):
                        fecha = trans.get('fecha', 'N/A')
                        canal = trans.get('canal', 'Desconocido')
                        valor = trans.get('valor_total', 0)
                        respuesta += f"{idx}. [{fecha}] {canal}: ${valor:,.0f}\n"

                    respuesta += "\n✅ Registros desde PostgreSQL en tiempo real."

                    return {
                        "intent": "documento_query",
                        "message": respuesta
                    }
            except Exception as e:
                logger.error(f"Error obteniendo datos de documentos: {e}")

        response = await self._generate_document_response(query)

        return {
            "message": response,
            "intent": "document_management",
            "agent": "document_manager_agent",
        }

    async def _generate_document_response(self, query: str) -> str:
        """Generar respuesta de gestión documental con Ollama"""
        try:
            from ..ollama_client import OllamaClient
            from ..system_prompts import get_system_prompt

            ollama = OllamaClient()
            system_prompt = get_system_prompt("document_manager_agent")

            prompt_ollama = f"""{system_prompt}

Consulta Documental: {query}

Proporciona clasificación, organización y políticas de retención documental."""

            logger.info("📑 Llamando a Ollama para gestión documental...")
            respuesta = await ollama.generar("glm4:9b", prompt_ollama)
            return respuesta
        except Exception as e:
            logger.error(f"Ollama error en DocumentManagerAgent: {e}")
            return "📑 Gestor Documental operativo. Clasifica y organiza documentos empresariales."
