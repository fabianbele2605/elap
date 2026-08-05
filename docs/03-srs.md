# Libro 3 — Software Requirements Specification (SRS)
## Enterprise Local AI Platform (ELAP)

**Versión:** 1.0 | **Estándar de referencia:** IEEE 830 / ISO-IEC-IEEE 29148 (adaptado) | **Depende de:** Libro 2 (BRD)

---

## 1. Objetivo

Especificar los requisitos funcionales y no funcionales del sistema con el nivel de detalle suficiente para que ingeniería pueda diseñar la arquitectura (Libro 4) directamente a partir de este documento.

## 2. Convención de identificadores

`RF-XXX` = Requisito Funcional, `RNF-XXX` = Requisito No Funcional. Cada uno tiene prioridad `MUST` / `SHOULD` / `COULD` (MoSCoW).

## 3. Requisitos funcionales

### 3.1 Gestión de agentes

| ID | Requisito | Prioridad |
|---|---|---|
| RF-001 | El sistema debe permitir crear un agente a partir de una plantilla estándar (nombre, objetivo, herramientas, memoria, permisos) | MUST |
| RF-002 | El sistema debe permitir activar/desactivar un agente sin reiniciar la plataforma | MUST |
| RF-003 | El sistema debe permitir que un agente delegue una subtarea a otro agente | SHOULD |
| RF-004 | El sistema debe registrar el historial de conversación de cada agente por usuario | MUST |
| RF-005 | El sistema debe permitir clonar un agente existente como base para uno nuevo | COULD |

### 3.2 Motor de modelos (Model Runtime)

| ID | Requisito | Prioridad |
|---|---|---|
| RF-010 | El sistema debe permitir cargar y descargar modelos locales (GGUF vía llama.cpp/Ollama) sin reiniciar el sistema | MUST |
| RF-011 | El sistema debe permitir asignar un modelo distinto por agente (ej. modelo de código para el agente Programador) | MUST |
| RF-012 | El sistema debe detectar automáticamente la disponibilidad de GPU NVIDIA y usarla si existe, o degradar a CPU | MUST |
| RF-013 | El sistema debe soportar streaming de tokens hacia la interfaz de usuario | MUST |

### 3.3 Memoria y contexto

| ID | Requisito | Prioridad |
|---|---|---|
| RF-020 | El sistema debe mantener memoria de corto plazo (conversación activa) por agente/usuario | MUST |
| RF-021 | El sistema debe mantener memoria de largo plazo persistente vía base vectorial | MUST |
| RF-022 | El sistema debe permitir búsqueda semántica sobre documentos empresariales indexados (RAG) | MUST |
| RF-023 | El sistema debe permitir al administrador purgar o exportar la memoria de un agente | SHOULD |

### 3.4 Herramientas (Tool Engine)

| ID | Requisito | Prioridad |
|---|---|---|
| RF-030 | El sistema debe permitir registrar herramientas nuevas vía plugins sin recompilar el núcleo | MUST |
| RF-031 | El sistema debe validar los permisos del usuario/agente antes de ejecutar cualquier herramienta | MUST |
| RF-032 | El sistema debe soportar herramientas de lectura/escritura de archivos, Office, PDF, SQL, correo, Git | MUST |
| RF-033 | El sistema debe permitir descubrir automáticamente herramientas expuestas por un servidor MCP | SHOULD |

### 3.5 Seguridad y administración

| ID | Requisito | Prioridad |
|---|---|---|
| RF-040 | El sistema debe implementar RBAC a nivel de usuario, agente y herramienta | MUST |
| RF-041 | El sistema debe registrar en un log de auditoría inmutable toda acción que modifique datos | MUST |
| RF-042 | El sistema debe permitir respaldo y restauración completa (configuración + memoria + modelos) | MUST |
| RF-043 | El sistema debe soportar autenticación local (usuario/contraseña) y, opcionalmente, SSO empresarial (LDAP/AD) | SHOULD |

### 3.6 Interfaz de usuario

| ID | Requisito | Prioridad |
|---|---|---|
| RF-050 | El sistema debe ofrecer un Dashboard con estado de agentes, modelos y recursos de hardware | MUST |
| RF-051 | El sistema debe ofrecer un Workflow Builder visual para encadenar tareas entre agentes | SHOULD |
| RF-052 | El sistema debe ofrecer un Prompt Builder para personalizar el comportamiento de un agente sin editar código | MUST |
| RF-053 | El sistema debe ofrecer un Resource Monitor (CPU/GPU/RAM) en tiempo real | MUST |

## 4. Requisitos no funcionales

| ID | Categoría | Requisito | Métrica objetivo |
|---|---|---|---|
| RNF-001 | Rendimiento | Latencia de primer token en hardware de referencia (CPU 8 núcleos, 16GB RAM, modelo 7B cuantizado Q4) | < 3s |
| RNF-002 | Disponibilidad | Uptime del núcleo (Rust) independiente de fallos del AI Runtime (Python) | El core no debe caer si el runtime de IA falla |
| RNF-003 | Seguridad | Cifrado de datos en reposo | AES-256 |
| RNF-004 | Seguridad | Cifrado de datos en tránsito (IPC entre Rust y Python) | TLS o socket local con autenticación |
| RNF-005 | Portabilidad | Sistemas operativos soportados | Linux Ubuntu 22.04+ (prioritario), Windows 10/11 |
| RNF-006 | Escalabilidad | Usuarios concurrentes soportados en instalación de referencia (16 núcleos, 64GB RAM, 1 GPU) | 50 usuarios concurrentes |
| RNF-007 | Mantenibilidad | Cobertura de tests automatizados en el núcleo Rust | > 80% |
| RNF-008 | Observabilidad | Toda métrica de telemetría debe quedar dentro del perímetro local (sin envío externo) | 100% local |
| RNF-009 | Instalación | Tiempo de instalación en hardware limpio | < 30 min (ver Libro 1, sección 9) |
| RNF-010 | Recuperación | RTO (Recovery Time Objective) tras fallo del AI Runtime | < 10s (reinicio automático del servicio Python) |

## 5. Casos de uso representativos

### CU-01: Consulta a un agente especializado
**Actor:** Usuario de negocio.
**Flujo:** Usuario abre la app → selecciona agente "Contabilidad" → escribe consulta → el core Rust valida permisos → enruta al AI Runtime → el runtime consulta memoria vectorial + modelo → responde con streaming → se registra en log de auditoría.

### CU-02: Delegación entre agentes
**Actor:** Agente "Ventas" necesita datos de "Inventario".
**Flujo:** Agente Ventas emite solicitud de delegación → orquestador valida permisos cruzados → agente Inventario procesa y responde → Ventas incorpora la respuesta a su contexto → usuario recibe respuesta consolidada.

### CU-03: Instalación de un plugin de terceros
**Actor:** Administrador de plataforma.
**Flujo:** Administrador sube paquete de plugin firmado → sistema valida firma y manifiesto de permisos solicitados → administrador aprueba permisos → plugin queda disponible para asignar a agentes.

## 6. Matriz de trazabilidad (extracto)

| Requisito de negocio (BRD) | Requisito funcional/no funcional (SRS) |
|---|---|
| BR-01 (offline) | RNF-008, RF-012 |
| BR-02 (privacidad) | RNF-003, RNF-004, RNF-008 |
| BR-05 (auditoría) | RF-041 |
| BR-06 (sin GPU) | RF-012, RNF-001 |
| BR-10 (RBAC) | RF-031, RF-040 |

## 7. Supuestos y dependencias

- Se asume disponibilidad de modelos open-weight compatibles con licencias comerciales (Llama, Qwen, Mistral, etc. — ver Libro 7 para la comparación).
- Se asume que el cliente provee hardware mínimo viable (ver RNF-001 y RF-012).
- Dependencia externa: Ollama/llama.cpp como motor de inferencia (ver Libro 4 y 7).

---
**Siguiente documento:** Libro 4 — Software Architecture Document (SAD).
