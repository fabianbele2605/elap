"""Schemas para documentos estructurados"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class ContractData:
    """Datos para contrato laboral"""
    empresa: str
    empleado: str
    cargo: str
    salario: float
    fecha_inicio: str
    fecha_vigencia: str = "Indefinido"
    beneficios: List[str] = field(default_factory=list)
    responsabilidades: List[str] = field(default_factory=list)
    ai_content: str = ""
    clausulas_adicionales: str = ""


@dataclass
class ReportData:
    """Datos para reporte empresarial"""
    titulo: str
    empresa: str
    periodo: str
    seccion_ejecutiva: str
    contenido_ia: str
    metricas: Dict[str, Any] = field(default_factory=dict)
    graficos: List[str] = field(default_factory=list)
    conclusiones: str = ""
    firma_autorizado: str = ""


@dataclass
class InvoiceData:
    """Datos para factura"""
    numero: str
    empresa_emisor: str
    cliente: str
    fecha_emision: str
    fecha_vencimiento: str
    items: List[Dict[str, Any]] = field(default_factory=list)
    subtotal: float = 0.0
    impuesto: float = 0.0
    total: float = 0.0
    condiciones_pago: str = ""
    notas: str = ""


@dataclass
class DocumentRequest:
    """Request para generar documento"""
    document_type: str  # contract, report, invoice, etc
    format: str  # word, pdf, excel, powerpoint
    theme: str  # andina_foods, default, etc
    data: Dict[str, Any]
    language: str = "es"
    sign: bool = False
    watermark: Optional[str] = None
