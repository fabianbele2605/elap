"""Document Engine - Generador de documentos profesionales"""

from .core import DocumentEngine
from .schemas import ContractData, ReportData, InvoiceData, DocumentRequest

__all__ = [
    "DocumentEngine",
    "ContractData",
    "ReportData",
    "InvoiceData",
    "DocumentRequest",
]

__version__ = "1.0.0"
