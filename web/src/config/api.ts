/**
 * Configuración de API
 * Cambio global para frontend cuando está en producción o detrás de tunnel
 */

// ✅ Para desarrollo local
// export const API_BASE_URL = "http://localhost:5000";

// ✅ Para producción con Cloudflare Tunnel
export const API_BASE_URL = "https://dock-potatoes-volunteer-caught.trycloudflare.com";

/**
 * Uso en componentes:
 *
 * import { API_BASE_URL } from '@/config/api';
 *
 * const response = await fetch(`${API_BASE_URL}/api/agents/finance/execute`, {
 *   method: 'POST',
 *   // ...
 * });
 */
