import { API_BASE_URL } from '../../config/api';
const API_BASE = '${API_BASE_URL}';  // Python REST API

export interface Agent {
  id: string;
  nombre: string;
  rol: string;
  estado: string;
  progreso: number;
  modelo: string;
}

export interface CreateAgentPayload {
  nombre: string;
  rol: string;
  objetivo: string;
}

// Agentes
export async function listarAgentes(): Promise<Agent[]> {
  try {
    const res = await fetch(`${API_BASE}/api/agents`);
    if (!res.ok) throw new Error(`Error ${res.status}`);
    const data = await res.json();
    return data.agents || data.agentes || [];
  } catch (err) {
    console.error('Error listando agentes:', err);
    return [];
  }
}

export async function crearAgente(payload: CreateAgentPayload): Promise<Agent | null> {
  try {
    const res = await fetch(`${API_BASE}/api/agents`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error(`Error ${res.status}`);
    const data = await res.json();
    return data.agente || null;
  } catch (err) {
    console.error('Error creando agente:', err);
    return null;
  }
}

export async function obtenerAgente(id: string): Promise<Agent | null> {
  try {
    const res = await fetch(`${API_BASE}/agents/${id}`);
    if (!res.ok) throw new Error(`Error ${res.status}`);
    const data = await res.json();
    return data.agente || null;
  } catch (err) {
    console.error('Error obteniendo agente:', err);
    return null;
  }
}

export async function eliminarAgente(id: string): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/agents/${id}`, { method: 'DELETE' });
    return res.ok;
  } catch (err) {
    console.error('Error eliminando agente:', err);
    return false;
  }
}

export async function ejecutarAgente(id: string, prompt: string): Promise<any> {
  try {
    const res = await fetch(`${API_BASE}/agents/${id}/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt }),
    });
    if (!res.ok) throw new Error(`Error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error('Error ejecutando agente:', err);
    return null;
  }
}

export async function obtenerEstado(id: string): Promise<any> {
  try {
    const res = await fetch(`${API_BASE}/agents/${id}/status`);
    if (!res.ok) throw new Error(`Error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error('Error obteniendo estado:', err);
    return null;
  }
}

// WebSocket Streaming
export function monitorearAgente(
  id: string,
  onMessage: (data: any) => void,
  onError: (err: any) => void
): WebSocket | null {
  try {
    const ws = new WebSocket(`ws://localhost:3000/agents/${id}/watch`);
    ws.onmessage = (evt) => onMessage(JSON.parse(evt.data));
    ws.onerror = (err) => onError(err);
    return ws;
  } catch (err) {
    onError(err);
    return null;
  }
}

export function ejecutarAgentStreaming(
  id: string,
  prompt: string,
  onData: (chunk: string) => void,
  onComplete: () => void,
  onError: (err: any) => void
): WebSocket | null {
  try {
    const ws = new WebSocket(`ws://localhost:3000/agents/${id}/execute/stream`);
    ws.onopen = () => ws.send(JSON.stringify({ prompt }));
    ws.onmessage = (evt) => onData(evt.data);
    ws.onclose = () => onComplete();
    ws.onerror = (err) => onError(err);
    return ws;
  } catch (err) {
    onError(err);
    return null;
  }
}

// === Historial de conversaciones ===
export async function apiCall(
  method: 'GET' | 'POST' | 'DELETE',
  endpoint: string,
  body?: any
): Promise<any> {
  try {
    const options: RequestInit = {
      method,
      headers: { 'Content-Type': 'application/json' }
    };
    if (body) options.body = JSON.stringify(body);

    // Asegurar que el endpoint tenga /api como prefijo
    const fullEndpoint = endpoint.startsWith('/api') ? endpoint : `/api${endpoint}`;
    const res = await fetch(`${API_BASE}${fullEndpoint}`, options);
    if (!res.ok) throw new Error(`Error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error(`Error en ${method} ${endpoint}:`, err);
    throw err;
  }
}
