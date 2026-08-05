# Libro 1 — Product Vision Document (PVD)
## Enterprise Local AI Platform (ELAP)

**Versión:** 1.0 | **Estado:** Aprobado para siguiente fase | **Owner:** Chief Software Architect

---

## 1. Objetivo del documento

Definir la visión, el problema, el mercado y la propuesta de valor de ELAP antes de tocar una línea de código. Este documento es la fuente de verdad para todas las decisiones posteriores de producto y arquitectura.

## 2. Alcance

Cubre: visión de producto, problema a resolver, usuarios objetivo, propuesta de valor, diferenciación competitiva, principios de diseño y criterios de éxito.
No cubre: detalle técnico de implementación (ver Libro 4, SAD) ni requisitos funcionales exhaustivos (ver Libro 3, SRS).

## 3. Declaración de visión

> ELAP es una plataforma de escritorio, 100% local y offline-first, que permite a cualquier empresa desplegar agentes de IA especializados por rol de negocio, sin enviar un solo byte de información a servidores externos, con el mismo nivel de control, auditoría y personalización que un producto empresarial cerrado — pero corriendo dentro de su propia infraestructura.

## 4. El problema

| Problema actual | Consecuencia |
|---|---|
| Las PYMEs y empresas reguladas no pueden usar ChatGPT/Copilot/Gemini para datos sensibles | Pérdida de productividad, uso de shadow IT no auditado |
| Las soluciones "IA local" existentes (Ollama, LM Studio) son herramientas de desarrollador, no productos empresariales | Adopción limitada a equipos técnicos |
| No existe un framework maduro de "agentes por rol" que funcione 100% on-premise | Cada empresa reinventa la rueda con scripts ad-hoc |
| El costo recurrente de APIs de IA cloud escala con el uso, no con el valor entregado | OPEX impredecible para PYMEs |

## 5. Usuarios objetivo

| Perfil | Necesidad principal |
|---|---|
| PYME (10–200 empleados) | Adoptar IA sin exponer datos de clientes/contratos, con bajo costo de entrada |
| Empresa regulada (salud, legal, financiero) | Cumplimiento normativo estricto (datos nunca salen del perímetro) |
| Administrador de TI interno | Instalar, configurar y mantener sin depender de un vendor externo |
| Consultor / integrador (ej. BBLABS) | Desplegar la plataforma en múltiples clientes como oferta de servicio |

## 6. Propuesta de valor

1. **Privacidad absoluta**: ningún dato sale de la red de la empresa.
2. **Costo predecible**: sin cobro por token; el costo es infraestructura propia.
3. **Especialización por rol**: agentes preconfigurados (Ventas, RRHH, Contabilidad, TI, Legal, etc.) en vez de un chatbot genérico.
4. **Extensible sin tocar el núcleo**: arquitectura de plugins para herramientas y agentes nuevos.
5. **Instalación como software profesional**: no es un notebook de Jupyter ni un script; es un instalador con GUI.

## 7. Diferenciación frente a soluciones cerradas

| Criterio | ChatGPT/Copilot/Gemini/Claude (cloud) | ELAP (local) |
|---|---|---|
| Privacidad de datos | Datos procesados en servidores del proveedor | Datos nunca salen de la empresa |
| Costo | Por uso/token, escala con volumen | Costo fijo de infraestructura |
| Disponibilidad offline | No | Sí |
| Personalización profunda por rol/empresa | Limitada (prompts, GPTs) | Total (agentes, memoria, herramientas propias) |
| Calidad del modelo (razonamiento general) | Superior (modelos frontier) | Menor, pero suficiente para tareas verticales bien acotadas |
| Latencia | Depende de red | Depende de hardware local, potencialmente menor |
| Mantenimiento | Cero (SaaS) | Requiere equipo de TI o consultor |

**Cuándo conviene IA local (ELAP):** datos sensibles/regulados, control de costos a largo plazo, necesidad de operar sin internet, personalización profunda, cumplimiento normativo estricto.

**Cuándo NO conviene:** se necesita el máximo nivel de razonamiento general disponible en el mercado, no hay presupuesto para hardware (GPU) ni para mantenimiento, el volumen de uso es tan bajo que el costo cloud es marginal.

## 8. Principios de diseño (no negociables)

1. **Local-first**: debe funcionar sin conexión a internet.
2. **Modularidad estricta**: cualquier componente se reemplaza sin afectar al resto (ver Libro 4).
3. **Rust para núcleo, Python exclusivamente para IA**: frontera de responsabilidad clara (ver Libro 4, sección 6).
4. **Cero edición de código para el usuario final**: toda configuración vía GUI.
5. **Extensibilidad vía plugins**, no vía fork del código base.
6. **Seguridad por defecto**: RBAC, cifrado y auditoría desde el día uno, no como añadido posterior.

## 9. Criterios de éxito (nivel producto)

| Métrica | Objetivo Fase MVP | Objetivo Fase Producción |
|---|---|---|
| Tiempo de instalación (bare metal → agente funcionando) | < 30 min | < 10 min |
| Agentes de rol disponibles out-of-the-box | 5 | 20+ |
| Operación 100% offline verificada | Sí | Sí |
| Hardware mínimo soportado | CPU only, 16GB RAM | CPU only, 8GB RAM (modelos cuantizados) |
| Incidentes de fuga de datos | 0 | 0 |

## 10. Riesgos de producto (alto nivel)

- Percepción de "calidad inferior" frente a IA cloud si se comunica mal la propuesta de valor.
- Dependencia del hardware del cliente (GPU disponible o no) para la experiencia de usuario.
- Curva de adopción: usuarios acostumbrados a UX de ChatGPT esperan la misma fluidez con hardware limitado.

## 11. Roadmap de negocio (resumen — detalle en Libro 4 y futuro Libro de Roadmap técnico)

Fase 0 Investigación → Fase 1 Arquitectura → Fase 2 Prototipo → Fase 3 MVP → Fase 4 Beta → Fase 5 Producción → Fase 6 Marketplace de agentes → Fase 7 Enterprise → Fase 8 Alta disponibilidad → Fase 9 Escalabilidad.

## 12. Checklist de aprobación de este documento

- [x] Problema validado con al menos un caso de uso real (BBLABS / PYMEs)
- [x] Usuarios objetivo definidos
- [x] Diferenciación competitiva justificada con tabla comparativa
- [x] Principios de diseño no negociables establecidos
- [ ] Validación con al menos un cliente piloto (pendiente)

---
**Siguiente documento:** Libro 2 — Business Requirements Document.
