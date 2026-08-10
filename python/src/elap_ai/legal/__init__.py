"""Legal Knowledge System - Búsqueda inteligente de leyes colombianas actualizadas

Proporciona:
- Búsqueda en APIs oficiales colombianas
- Caché en SQLite para respuestas rápidas
- Web search para fuentes no disponibles
- Actualización automática de leyes
- Sincronización con canales oficiales

Nota: Requiere apscheduler para el scheduler. Sin él, funciona búsqueda manual.
"""

from .official_apis import OfficialAPIs
from .legal_search_engine import LegalSearchEngine

try:
    from .update_scheduler import LeyesUpdateScheduler, leyes_scheduler
    HAS_SCHEDULER = True
except ImportError:
    HAS_SCHEDULER = False
    leyes_scheduler = None
    LeyesUpdateScheduler = None

__all__ = [
    "OfficialAPIs",
    "LegalSearchEngine",
    "LeyesUpdateScheduler",
    "leyes_scheduler",
    "HAS_SCHEDULER",
]
