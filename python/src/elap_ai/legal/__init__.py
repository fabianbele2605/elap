"""Legal Knowledge System - Búsqueda inteligente de leyes colombianas actualizadas

Proporciona:
- Búsqueda en APIs oficiales colombianas
- Caché en Qdrant para respuestas rápidas
- Web search para fuentes no disponibles
- Actualización automática de leyes
- Sincronización con canales oficiales
"""

from .official_apis import OfficialAPIs
from .legal_search_engine import LegalSearchEngine
from .update_scheduler import LeyesUpdateScheduler, leyes_scheduler

__all__ = [
    "OfficialAPIs",
    "LegalSearchEngine",
    "LeyesUpdateScheduler",
    "leyes_scheduler",
]
