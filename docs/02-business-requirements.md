# Libro 2 — Business Requirements Document (BRD)
## Enterprise Local AI Platform (ELAP)

**Versión:** 1.0 | **Depende de:** Libro 1 (Product Vision)

---

## 1. Objetivo

Traducir la visión de producto en requisitos de negocio verificables: qué debe lograr ELAP para la empresa que lo adopta, independientemente de cómo se implemente técnicamente.

## 2. Alcance

Requisitos de negocio, actores, reglas de negocio, restricciones comerciales y KPIs de negocio. No incluye requisitos funcionales de sistema (ver Libro 3, SRS).

## 3. Actores del negocio

| Actor | Rol |
|---|---|
| Administrador de la plataforma | Instala, configura roles/permisos, gestiona modelos |
| Usuario de negocio | Interactúa con un agente específico (Ventas, RRHH, etc.) |
| Consultor/Integrador (BBLABS) | Despliega y personaliza ELAP para un cliente |
| Auditor de seguridad/cumplimiento | Revisa logs, permisos y políticas |
| Desarrollador de plugins | Extiende la plataforma con nuevas herramientas/agentes |

## 4. Requisitos de negocio (BR)

| ID | Requisito | Justificación |
|---|---|---|
| BR-01 | La plataforma debe operar sin conexión a internet en modo normal | Cumplimiento y privacidad (Libro 1, sección 7) |
| BR-02 | Ningún dato de la empresa debe transmitirse a servicios de terceros por defecto | Requisito no negociable de privacidad |
| BR-03 | El sistema debe soportar múltiples agentes especializados por rol de negocio operando simultáneamente | Núcleo de la propuesta de valor |
| BR-04 | La instalación y configuración debe ser realizable por un administrador de TI sin conocimientos de IA/ML | Reduce barrera de adopción en PYMEs |
| BR-05 | El sistema debe permitir auditar quién hizo qué, cuándo y con qué agente | Requisito de cumplimiento (ver Libro 15, Security Architecture) |
| BR-06 | El sistema debe funcionar en hardware sin GPU dedicada, con degradación aceptable de rendimiento | Accesibilidad para PYMEs sin presupuesto de hardware |
| BR-07 | Debe ser posible añadir nuevos agentes o herramientas sin modificar el núcleo del sistema | Sostenibilidad y escalabilidad comercial (marketplace, Fase 6) |
| BR-08 | El costo operativo no debe escalar linealmente con el volumen de uso (a diferencia de APIs cloud por token) | Diferenciador comercial clave |
| BR-09 | El sistema debe permitir respaldo y restauración completa de la configuración y memoria de los agentes | Continuidad de negocio |
| BR-10 | Debe existir un mecanismo de control de acceso basado en roles (RBAC) a nivel de agente y de herramienta | Seguridad empresarial |

## 5. Reglas de negocio

- **RN-01**: Un agente nunca puede ejecutar una herramienta para la que el usuario solicitante no tiene permiso, independientemente de lo que el modelo de IA "decida".
- **RN-02**: Toda acción de un agente que modifique datos (escritura, envío de correo, etc.) debe quedar registrada en el log de auditoría de forma inmutable.
- **RN-03**: Un plugin de tercero no puede acceder a los datos de otro plugin salvo autorización explícita del administrador.
- **RN-04**: La desconexión de internet no debe degradar ninguna funcionalidad core (solo funcionalidades opcionales marcadas como "online-only", si existieran).

## 6. Restricciones comerciales

- Debe poder venderse/desplegarse como producto on-premise (licencia perpetua o suscripción de soporte), no exclusivamente SaaS.
- Debe ser viable para un integrador (como BBLABS) desplegarlo en múltiples clientes con configuraciones aisladas entre sí.
- El modelo de negocio de "Marketplace de agentes" (Fase 6) requiere que los agentes/plugins de terceros puedan empaquetarse y distribuirse de forma segura.

## 7. KPIs de negocio

| KPI | Descripción | Meta orientativa |
|---|---|---|
| Time-to-value | Tiempo desde instalación hasta primer agente productivo | < 1 día |
| Costo total de propiedad (TCO) a 3 años vs. alternativa cloud equivalente | Comparación de costos | Menor a partir del mes 8–12 de uso intensivo |
| Tasa de incidentes de seguridad/fuga de datos | Auditoría | 0 |
| Número de agentes activos por cliente | Adopción interna | Creciente mes a mes |
| Retención de clientes (para modelo de soporte/suscripción) | Negocio | > 85% anual |

## 8. Fuera de alcance (explícito)

- No se pretende igualar la calidad de razonamiento de modelos frontier cloud (GPT-5, Claude Opus, Gemini) en tareas generales abiertas.
- No se pretende ofrecer entrenamiento de modelos desde cero; se usan modelos open-weight existentes (ver Libro 7).
- No se pretende ser una plataforma de robótica industrial completa; ROS2 queda como integración opcional futura, no como núcleo (ver decisión en Libro 4).

## 9. Trazabilidad con Libro 1

Cada BR de este documento debe poder rastrearse a un principio de diseño o criterio de éxito del Product Vision Document. Ejemplo: BR-01 y BR-02 → Principio de diseño "Local-first" (Libro 1, sección 8.1).

---
**Siguiente documento:** Libro 3 — Software Requirements Specification (SRS).
