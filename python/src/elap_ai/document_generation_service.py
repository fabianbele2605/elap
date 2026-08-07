"""
Servicio de generación de documentos para Fase 3.

Maneja:
- Generación de 15 documentos personalizados
- Auto-indexación en RAG
- Tracking de estado
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib

from .document_templates import generar_todos_documentos, DOCUMENT_TEMPLATES
from .memory.vector_db import VectorStore
from .tools.documents.writers import DocumentGenerator


class GenerationStatus:
    """Mantiene estado de una generación en progreso."""

    def __init__(self, company_id: str, company_name: str):
        self.company_id = company_id
        self.company_name = company_name
        self.start_time = datetime.now()
        self.documents: Dict[str, Dict[str, Any]] = {}
        self.overall_status = "generating"
        self.error: Optional[str] = None

    def add_document(self, doc_id: str, title: str, template_name: str):
        """Agrega un documento al tracking."""
        self.documents[doc_id] = {
            "id": doc_id,
            "title": title,
            "template_name": template_name,
            "status": "pending",
            "progress": 0,
            "content": None,
            "indexed_in_rag": "no",
            "error": None,
        }

    def update_document(
        self,
        doc_id: str,
        status: str,
        progress: int = None,
        content: str = None,
        error: str = None,
    ):
        """Actualiza estado de un documento."""
        if doc_id in self.documents:
            if status:
                self.documents[doc_id]["status"] = status
            if progress is not None:
                self.documents[doc_id]["progress"] = progress
            if content:
                self.documents[doc_id]["content"] = content
            if error:
                self.documents[doc_id]["error"] = error

    def mark_indexed(self, doc_id: str):
        """Marca un documento como indexado en RAG."""
        if doc_id in self.documents:
            self.documents[doc_id]["indexed_in_rag"] = "yes"

    def get_progress_percentage(self) -> float:
        """Retorna porcentaje de progreso (0-100)."""
        if not self.documents:
            return 0.0
        completed = sum(
            1 for doc in self.documents.values() if doc["status"] == "ready"
        )
        return (completed / len(self.documents)) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para respuesta gRPC."""
        completed = sum(
            1 for doc in self.documents.values() if doc["status"] == "ready"
        )
        indexed = sum(
            1 for doc in self.documents.values() if doc["indexed_in_rag"] == "yes"
        )

        return {
            "company_id": self.company_id,
            "overall_status": self.overall_status,
            "documents": list(self.documents.values()),
            "total_documents": len(self.documents),
            "completed_documents": completed,
            "documents_indexed": indexed,
            "progress_percentage": self.get_progress_percentage(),
            "error": self.error,
        }


class DocumentGenerationService:
    """Servicio principal de generación de documentos."""

    def __init__(self, vector_store: Optional[VectorStore] = None):
        self.vector_store = vector_store
        self.doc_generator = DocumentGenerator()
        self.generations: Dict[str, GenerationStatus] = {}

    async def generate_documents(
        self, company_config: Dict[str, Any], template_names: List[str] = None
    ) -> Dict[str, Any]:
        """
        Genera todos (o especificados) documentos para una empresa.

        Args:
            company_config: Configuración de empresa (nombreEmpresa, sector, etc.)
            template_names: Lista de templates a generar. Si None, genera todos.

        Returns:
            Dict con estado de generación completa
        """
        company_id = hashlib.md5(
            company_config.get("nombreEmpresa", "").encode()
        ).hexdigest()[:8]
        company_name = company_config.get("nombreEmpresa", "Unknown")

        # Crear rastreador de estado
        status = GenerationStatus(company_id, company_name)
        self.generations[company_id] = status

        try:
            # Determinar qué templates generar
            if not template_names:
                template_names = list(DOCUMENT_TEMPLATES.keys())

            # Inicializar documentos en tracking
            doc_id_map = {}
            for idx, template_name in enumerate(template_names):
                if template_name not in DOCUMENT_TEMPLATES:
                    continue
                title = self._get_template_title(template_name)
                doc_id = f"doc_{idx:02d}"
                doc_id_map[template_name] = doc_id
                status.add_document(doc_id, title, template_name)

            # Generar documentos en paralelo (pero con límite de concurrencia)
            tasks = [
                self._generate_single_document(
                    company_config, template_name, doc_id_map[template_name], status
                )
                for template_name in template_names
                if template_name in DOCUMENT_TEMPLATES
            ]

            # Ejecutar hasta 3 documentos en paralelo
            for i in range(0, len(tasks), 3):
                batch = tasks[i : i + 3]
                await asyncio.gather(*batch)

            # Marcar como completado
            status.overall_status = "completed"

            return status.to_dict()

        except Exception as e:
            status.overall_status = "error"
            status.error = str(e)
            return status.to_dict()

    async def _generate_single_document(
        self,
        company_config: Dict[str, Any],
        template_name: str,
        doc_id: str,
        status: GenerationStatus,
    ) -> None:
        """Genera un documento individual."""
        try:
            # Marcar como en progreso
            status.update_document(doc_id, status="generating", progress=0)
            await asyncio.sleep(0.1)  # Simular I/O

            # Renderizar template
            status.update_document(doc_id, progress=25)
            template_class = DOCUMENT_TEMPLATES.get(template_name)
            if not template_class:
                raise ValueError(f"Template no encontrado: {template_name}")

            content = template_class.render(company_config)
            status.update_document(doc_id, progress=50, content=content)

            # Aquí iría la generación real de PDF/Excel
            # Por ahora, solo guardamos el contenido
            status.update_document(doc_id, progress=75)

            # Auto-index en RAG si está disponible
            if self.vector_store:
                try:
                    title = self._get_template_title(template_name)
                    # Chunking simple (cada párrafo)
                    chunks = [
                        p.strip()
                        for p in content.split("\n\n")
                        if p.strip() and len(p.strip()) > 50
                    ]

                    # Agregar a vector store
                    collection_name = f"company_{status.company_id}"
                    for chunk_idx, chunk in enumerate(chunks[:5]):  # Limitar a 5 chunks
                        self.vector_store.add_document(
                            collection_name,
                            f"{template_name}_chunk_{chunk_idx}",
                            chunk,
                            {"template": template_name, "title": title},
                        )

                    status.mark_indexed(doc_id)
                except Exception as e:
                    # Log pero continúa
                    print(f"Error indexando {template_name}: {e}")

            # Marcar como listo
            status.update_document(doc_id, status="ready", progress=100)

        except Exception as e:
            status.update_document(
                doc_id, status="error", progress=0, error=str(e)
            )

    def get_generation_status(self, company_id: str) -> Dict[str, Any]:
        """Obtiene estado de una generación en progreso o completada."""
        if company_id not in self.generations:
            return {
                "company_id": company_id,
                "overall_status": "not_found",
                "error": f"No generation found for company_id: {company_id}",
            }

        status = self.generations[company_id]
        return status.to_dict()

    @staticmethod
    def _get_template_title(template_name: str) -> str:
        """Obtiene el título legible de un template."""
        title_map = {
            "manual_empleado": "Manual del Empleado",
            "politica_vacaciones": "Política de Vacaciones",
            "codigo_conducta": "Código de Conducta",
            "presupuesto_anual": "Presupuesto Anual",
            "politica_gastos": "Política de Gastos",
            "politica_calidad": "Política de Calidad",
            "politica_ausencias": "Política de Ausencias",
            "procedimiento_contratacion": "Procedimiento de Contratación",
            "reportes_financieros": "Reportes Financieros",
            "matriz_procesos": "Matriz de Procesos",
            "procedimientos_operacionales": "Procedimientos Operacionales",
            "politica_compras": "Política de Compras",
            "terminos_condiciones": "Términos y Condiciones",
            "politica_privacidad": "Política de Privacidad",
            "estrategia_comercial": "Estrategia Comercial",
        }
        return title_map.get(template_name, template_name.replace("_", " ").title())
