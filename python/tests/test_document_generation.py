"""
Tests para DocumentGenerationService (Fase 3)
"""

import pytest
import asyncio
from datetime import datetime

from elap_ai.document_generation_service import (
    DocumentGenerationService,
    GenerationStatus,
)
from elap_ai.document_templates import DOCUMENT_TEMPLATES


@pytest.fixture
def service():
    """Fixture para DocumentGenerationService"""
    return DocumentGenerationService()


@pytest.fixture
def sample_company_config():
    """Configuración de empresa de prueba"""
    return {
        "nombreEmpresa": "Test Company",
        "sector": "Tecnología",
        "ubicacion": "Bogotá, Colombia",
        "anoFundacion": 2020,
        "website": "https://testcompany.com",
        "numEmpleados": 150,
        "departamentos": ["RRHH", "Finanzas", "Operaciones", "Ventas"],
        "ceo": "Juan Perez",
        "contactoRRHH": "maria@testcompany.com",
        "productos": ["Producto A", "Producto B"],
        "servicios": ["Servicio A", "Servicio B"],
        "clientesPrincipales": "Grandes empresas",
        "salarioPromedio": 3500000,
        "presupuestoAnual": 500000000,
        "crecimientoEsperado": "15-20%",
    }


class TestGenerationStatus:
    """Tests para la clase GenerationStatus"""

    def test_creation(self):
        """Test creación de GenerationStatus"""
        status = GenerationStatus("company_123", "Test Corp")
        assert status.company_id == "company_123"
        assert status.company_name == "Test Corp"
        assert status.overall_status == "generating"

    def test_add_document(self):
        """Test agregar documento"""
        status = GenerationStatus("company_123", "Test Corp")
        status.add_document("doc_001", "Test Document", "test_template")
        assert "doc_001" in status.documents
        assert status.documents["doc_001"]["status"] == "pending"

    def test_update_document(self):
        """Test actualizar documento"""
        status = GenerationStatus("company_123", "Test Corp")
        status.add_document("doc_001", "Test Document", "test_template")
        status.update_document("doc_001", status="generating", progress=50)
        assert status.documents["doc_001"]["status"] == "generating"
        assert status.documents["doc_001"]["progress"] == 50

    def test_progress_percentage(self):
        """Test cálculo de progreso"""
        status = GenerationStatus("company_123", "Test Corp")
        status.add_document("doc_001", "Doc 1", "template_1")
        status.add_document("doc_002", "Doc 2", "template_2")
        status.update_document("doc_001", status="ready")
        assert status.get_progress_percentage() == 50.0

    def test_mark_indexed(self):
        """Test marcar como indexado"""
        status = GenerationStatus("company_123", "Test Corp")
        status.add_document("doc_001", "Doc 1", "template_1")
        status.mark_indexed("doc_001")
        assert status.documents["doc_001"]["indexed_in_rag"] == "yes"

    def test_to_dict(self):
        """Test conversión a diccionario"""
        status = GenerationStatus("company_123", "Test Corp")
        status.add_document("doc_001", "Doc 1", "template_1")
        result = status.to_dict()
        assert result["company_id"] == "company_123"
        assert result["total_documents"] == 1
        assert result["completed_documents"] == 0


class TestDocumentGenerationService:
    """Tests para DocumentGenerationService"""

    @pytest.mark.asyncio
    async def test_generate_documents_all_templates(self, service, sample_company_config):
        """Test generar todos los documentos"""
        result = await service.generate_documents(sample_company_config)

        assert result["overall_status"] == "completed"
        assert result["total_documents"] == len(DOCUMENT_TEMPLATES)
        assert result["completed_documents"] == len(DOCUMENT_TEMPLATES)

    @pytest.mark.asyncio
    async def test_generate_documents_specific_templates(
        self, service, sample_company_config
    ):
        """Test generar documentos específicos"""
        template_names = ["manual_empleado", "presupuesto_anual"]
        result = await service.generate_documents(
            sample_company_config, template_names
        )

        assert result["overall_status"] == "completed"
        assert result["total_documents"] == 2

    @pytest.mark.asyncio
    async def test_generate_documents_empty_list(self, service, sample_company_config):
        """Test con lista vacía de templates (debe generar todos)"""
        result = await service.generate_documents(sample_company_config, [])

        assert result["total_documents"] == len(DOCUMENT_TEMPLATES)

    @pytest.mark.asyncio
    async def test_get_generation_status(self, service, sample_company_config):
        """Test obtener estado de generación"""
        # Generar primero
        gen_result = await service.generate_documents(sample_company_config)
        company_id = gen_result["company_id"]

        # Obtener estado
        status = service.get_generation_status(company_id)

        assert status["company_id"] == company_id
        assert status["overall_status"] == "completed"

    @pytest.mark.asyncio
    async def test_get_generation_status_not_found(self, service):
        """Test obtener estado de generación inexistente"""
        status = service.get_generation_status("nonexistent_id")

        assert status["overall_status"] == "not_found"
        assert "error" in status

    @pytest.mark.asyncio
    async def test_document_progress(self, service, sample_company_config):
        """Test que cada documento tenga progreso"""
        result = await service.generate_documents(sample_company_config)

        for doc in result["documents"]:
            assert doc["progress"] == 100
            assert doc["status"] == "ready"

    @pytest.mark.asyncio
    async def test_all_templates_generated(self, service, sample_company_config):
        """Test que se generen todos los templates correctos"""
        result = await service.generate_documents(sample_company_config)

        generated_templates = [doc["template_name"] for doc in result["documents"]]
        expected_templates = list(DOCUMENT_TEMPLATES.keys())

        assert set(generated_templates) == set(expected_templates)

    def test_get_template_title(self):
        """Test obtener títulos de templates"""
        titles = {
            "manual_empleado": "Manual del Empleado",
            "politica_vacaciones": "Política de Vacaciones",
            "codigo_conducta": "Código de Conducta",
        }

        for template_name, expected_title in titles.items():
            title = DocumentGenerationService._get_template_title(template_name)
            assert title == expected_title


class TestTemplateRendering:
    """Tests para renderizado de templates"""

    def test_all_templates_have_render_method(self):
        """Test que todos los templates tengan método render"""
        for template_name, template_class in DOCUMENT_TEMPLATES.items():
            assert hasattr(template_class, "render")
            assert callable(getattr(template_class, "render"))

    def test_template_render_with_config(self, sample_company_config):
        """Test renderizar template con configuración"""
        from elap_ai.document_templates import ManualDelEmpleadoTemplate

        content = ManualDelEmpleadoTemplate.render(sample_company_config)

        assert len(content) > 0
        assert sample_company_config["nombreEmpresa"] in content
        assert sample_company_config["sector"] in content

    def test_template_renders_without_error(self, sample_company_config):
        """Test que todos los templates rendericen sin error"""
        for template_name, template_class in DOCUMENT_TEMPLATES.items():
            try:
                content = template_class.render(sample_company_config)
                assert isinstance(content, str)
                assert len(content) > 100  # Debe tener contenido significativo
            except Exception as e:
                pytest.fail(f"Template {template_name} failed to render: {e}")

    def test_template_contains_company_info(self, sample_company_config):
        """Test que los templates contengan información de la empresa"""
        from elap_ai.document_templates import PresupuestoAnualTemplate

        content = PresupuestoAnualTemplate.render(sample_company_config)

        assert str(sample_company_config["salarioPromedio"]) in content or (
            str(int(sample_company_config["salarioPromedio"] * 1.1)) in content
        )


class TestIntegration:
    """Tests de integración"""

    @pytest.mark.asyncio
    async def test_full_workflow(self, service, sample_company_config):
        """Test flujo completo: generar → obtener estado"""
        # Generar documentos
        gen_result = await service.generate_documents(sample_company_config)
        company_id = gen_result["company_id"]

        # Obtener estado
        status = service.get_generation_status(company_id)

        # Validaciones
        assert status["company_id"] == company_id
        assert status["overall_status"] == "completed"
        assert status["total_documents"] == len(DOCUMENT_TEMPLATES)
        assert len(status["documents"]) == len(DOCUMENT_TEMPLATES)

    @pytest.mark.asyncio
    async def test_multiple_generations(self, service):
        """Test múltiples generaciones simultáneas"""
        configs = [
            {
                "nombreEmpresa": f"Company {i}",
                "sector": "Sector A",
                "ubicacion": "Bogotá",
                "anoFundacion": 2020,
                "numEmpleados": 100 + i * 10,
                "departamentos": ["RRHH"],
                "salarioPromedio": 3000000,
            }
            for i in range(3)
        ]

        # Generar en paralelo
        results = await asyncio.gather(
            *[service.generate_documents(config) for config in configs]
        )

        assert len(results) == 3
        assert all(r["overall_status"] == "completed" for r in results)
        assert len(set(r["company_id"] for r in results)) == 3  # IDs únicos


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
