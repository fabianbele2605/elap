# Registros de Decisión Arquitectónica (RDA)

**Estilo de documento**: RDA (Registro de Decisión Arquitectónica)  
**Versión**: 1.0-alpha  
**Fecha de creación**: 2026-08-04

---

## RDA-001: Usar Rust para el Motor Central

**Estado**: ✅ **Aceptada**

**Decisión**: La orquestación central, planificación de tareas y gestión de procesos se implementarán en **Rust**, no en Python, Go o C++.

**Contexto**:
Necesitamos una plataforma performante y segura en memoria que:
- Maneje solicitudes concurrentes (100+ agentes simultáneamente)
- Gestione procesos de forma segura (aislamiento de plugins)
- Se integre con el SO (E/S de archivos, detección GPU, señales de procesos)
- Se ejecute en hardware mínimo (PYMEs con 8GB RAM)

**Alternativas consideradas**:

| Lenguaje | Pros | Contras | Veredicto |
|----------|------|---------|---------|
| **Rust** | Seguro en memoria, rápido, Tokio async, buen acceso al SO | Curva de aprendizaje pronunciada | ✅ **ELEGIDO** |
| Python | Fácil de escribir, gran biblioteca de IA | Lento para el núcleo, GC, sobrecarga de memoria | ❌ No apto para núcleo |
| Go | Concurrencia fácil, compilación cruzada | Menos seguro en memoria, menos acceso al SO | ❌ 3er ecosistema innecesario |
| C++ | Muy rápido, control fino | Memoria insegura, complejo, desarrollo lento | ❌ Demasiado riesgoso |

**Factores de decisión**:
1. **Seguridad**: Rust previene categorías completas de bugs (memoria, race conditions)
2. **Rendimiento**: Sobrecarga mínima, sin pausas de GC
3. **Ecosistema**: El runtime async Tokio es superior a cualquier cosa en Python/Go
4. **Mantenibilidad**: Tipado fuerte, el compilador detecta errores temprano

**Consecuencias**:
- ✅ Núcleo confiable que puede correr meses sin reinicio
- ✅ Planificación de tareas rápida sin pausas de GC
- ⚠️ Rust tiene curva de aprendizaje (mitigar con mentoría, revisión de código)
- ⚠️ Tiempos de compilación más lentos que Go (aceptable, no es ruta crítica)

**RDA relacionadas**: RDA-002 (Python para IA)

---

## RDA-002: Usar Python exclusivamente para Motor de IA

**Estado**: ✅ **Aceptada**

**Decisión**: Todas las cargas de trabajo de IA/ML (inferencia, RAG, agentes, incrustaciones) se ejecutan en **proceso Python separado**, no en Rust.

**Contexto**:
- Inferencia de LLM: dominada por PyTorch, Transformers, bindings Python de llama.cpp
- RAG/incrustaciones: LangChain, LangGraph, clientes de ChromaDB
- Agentes: LangGraph es Python-first
- Madurez del ecosistema: Python es estándar de facto para IA

**Alternativas consideradas**:

| Enfoque | Pros | Contras | Veredicto |
|---------|------|---------|---------|
| **Proceso Python separado** | Ajuste del ecosistema, reiniciable independientemente, API gRPC tipada | Latencia de IPC | ✅ **ELEGIDO** |
| Rust + bindings de llama.cpp | Proceso integrado, baja latencia de IPC | Frameworks de agentes limitados, reinventar RAG | ❌ Demasiado trabajo |
| PyO3 (bindings Python en Rust) | Integración directa, baja latencia | Los crashes llevan al núcleo, acoplamiento fuerte | ❌ Inseguro |
| Go para IA | ??? | Sin librerías de IA establecidas en Go | ❌ Impráctica |

**Factores de decisión**:
1. **Ecosistema**: El ecosistema Python para IA es inmejorable
2. **Time-to-market**: Aprovechar librerías existentes (LangChain, LangGraph)
3. **Independencia**: El proceso Python puede fallar/reiniciarse sin afectar núcleo
4. **Especialización**: Separación clara de preocupaciones

**Consecuencias**:
- ✅ Puede aprovechar las mejores librerías de IA
- ✅ Los fallos de Python no crashean el núcleo Rust
- ✅ Puede actualizar Python sin recompilar Rust
- ⚠️ La IPC gRPC agrega ~5-10ms de latencia (aceptable para inferencia que toma 500ms+)
- ⚠️ Más complejidad operacional (dos procesos a gestionar)

**Mitigación**:
- Usar streaming gRPC para eficiencia
- Hacer benchmark de latencia de IPC en Fase 1
- Documentar requisitos operacionales

**RDA relacionadas**: RDA-001 (Rust core), RDA-003 (comunicación gRPC)

---

## RDA-003: Usar gRPC sobre socket Unix para comunicación Rust ↔ Python

**Estado**: ✅ **Aceptada**

**Decisión**: Motor Central Rust y Motor de IA Python se comunican vía **gRPC sobre socket de dominio Unix** (Linux) / named pipe (Windows), con encriptación TLS.

**Contexto**:
Dos procesos independientes necesitan comunicarse:
- Motor Central valida permisos, pide a Python procesar consulta
- Python transmite tokens de respuesta de vuelta
- Ambos corren en la misma máquina (principio local-first)

**Alternativas consideradas**:

| Método | Latencia | Tipado | Streaming | Complejidad | Seguridad IPC |
|--------|----------|--------|-----------|------------|-----------|
| **gRPC/socket** | ~5ms | ✅ Protobuf | ✅ Nativo | Moderada | ✅ Aislamiento de socket |
| HTTP/REST local | ~10ms | ⚠️ JSON | ❌ Chunked | Baja | ⚠️ Sobrecarga HTTP |
| ZeroMQ | ~2ms | ❌ Personalizado | ✅ Sí | Alta | ⚠️ Protocolo personalizado |
| Bindings PyO3 | <1ms | ✅ Tipado | ⚠️ Callbacks | Alta | ❌ Riesgo de memoria compartida |
| Unix pipes | ~3ms | ❌ Bytes sin procesar | ✅ Sí | Muy alta | ✅ Seguro |

**Factores de decisión**:
1. **API tipada**: Protocol Buffers hacen cumplir versionado, previenen desajustes
2. **Streaming**: Streaming gRPC nativo (importante para transmisión de tokens)
3. **Estándar**: Estándar de industria, probado en producción
4. **Seguridad de procesos**: Los procesos independientes pueden reiniciarse entre sí
5. **Seguridad**: Puede usar TLS sobre socket

**Consecuencias**:
- ✅ API type-safe entre lenguajes
- ✅ Puede versionar independientemente
- ✅ El reinicio de Python no requiere reinicio del Motor Central
- ✅ Streaming de respuestas soportado de forma nativa
- ⚠️ 5-10ms de latencia por llamada RPC
- ⚠️ Debugging más complejo (proceso separado)

**Mitigación**:
- Usar solicitudes en lote donde sea posible
- Implementar pooling de conexiones
- Registrar toda IPC en pista de auditoría

**RDA relacionadas**: RDA-001, RDA-002

---

## RDA-004: Usar Tauri para shell de escritorio (no Electron)

**Estado**: ✅ **Aceptada**

**Decisión**: Aplicación de escritorio construida con **Tauri** (backend Rust, frontend web), no Electron.

**Contexto**:
Necesitar GUI de escritorio para:
- Interfaz de chat del agente
- Gestión de configuración
- Monitoreo del sistema
- Autenticación del usuario

**Alternativas consideradas**:

| Framework | Tamaño binario | RAM | Backend | Velocidad dev | Veredicto |
|-----------|-------------|-----|---------|-----------|---------|
| **Tauri** | ~10MB | Bajo (WebKit) | Rust nativo | Buena | ✅ **ELEGIDO** |
| Electron | 150MB+ | Alto (Chromium) | Node.js | Muy buena | ❌ Demasiado hinchado |
| Qt | ~50MB | Medio | C++ | Lenta | ❌ Complejidad C++ |
| wxWidgets | ~30MB | Medio | C++ | Lenta | ❌ Tecnología antigua |
| Solo web | N/A | N/A | N/A | Muy buena | ❌ Necesita servidor (rompe offline) |

**Factores de decisión**:
1. **Tamaño**: 10MB vs 150MB es crítico para distribución en PYME
2. **RAM**: Importa en hardware del cliente (máquinas de 8GB)
3. **Backend nativo**: Código Rust directo, no JavaScript
4. **Capaz offline**: App de escritorio, no navegador web

**Consecuencias**:
- ✅ Huella mínima, startup rápido
- ✅ Usa WebKit del SO del cliente (no Chromium embebido)
- ✅ Puede escribir código adyacente a UI en Rust
- ⚠️ Diferencias de WebKit en SO (Windows usa Edge, macOS usa Safari)
- ⚠️ Comunidad más pequeña que Electron

**Mitigación**:
- Usar estándares web (HTML/CSS/TS) para UI (máxima compatibilidad)
- Probar en Windows/macOS/Linux
- Contribuir a comunidad Tauri

**RDA relacionadas**: RDA-001 (Rust)

---

## RDA-005: Usar Tokio para planificación async de tareas

**Estado**: ✅ **Aceptada**

**Decisión**: Planificación de tareas y operaciones async en Rust usan **Tokio**, no async-std u otros runtimes.

**Contexto**:
Motor Central necesita manejar:
- Solicitudes concurrentes a agentes (100+ simultáneamente)
- Trabajos de larga duración en background (cargar modelos, respaldos)
- Timers y planificación
- Spawning de procesos

**Alternativas consideradas**:

| Runtime | Throughput | Ecosistema | Madurez | Veredicto |
|---------|-----------|-----------|----------|---------|
| **Tokio** | Muy alto (millones/seg) | Excelente (gRPC, Hyper) | Listo para producción | ✅ **ELEGIDO** |
| async-std | Bueno | Ecosistema pequeño | Menos maduro | ❌ Comunidad más pequeña |
| embassy | Enfocado en embedded | Especializado | Menos general | ❌ No apto |

**Factores de decisión**:
1. **Estándar de industria**: Usado por empresas Rust (Discord, Cloudflare, etc.)
2. **Soporte del ecosistema**: gRPC (tonic) construido sobre Tokio
3. **Rendimiento**: Throughput excepcional para operaciones concurrentes
4. **Madurez**: Probado en producción

**Consecuencias**:
- ✅ Rendimiento excepcional para operaciones concurrentes
- ✅ Rico ecosistema de librerías
- ✅ Bien documentado, comunidad grande
- ⚠️ Curva de aprendizaje para async Rust
- ⚠️ Complejidad de debugging (stacktraces async)

**RDA relacionadas**: RDA-001 (Rust)

---

## RDA-006: SQLite para dev, PostgreSQL para empresa

**Estado**: ✅ **Aceptada**

**Decisión**: Aplicación soporta tanto **SQLite** (dev/usuario único) como **PostgreSQL** (empresa multi-usuario), con mismo esquema.

**Contexto**:
Diferentes escenarios de despliegue:
- **PYME**: Máquina única, base de datos única, <10GB datos
- **Empresa**: Múltiples servidores, usuarios concurrentes, requisitos HA

**Alternativas consideradas**:

| Base de datos | Dev | Empresa | Migración de esquema | Veredicto |
|------------|-----|--------|-----------------|---------|
| **SQLite + PostgreSQL** | ✅ | ✅ | Mismo esquema | ✅ **ELEGIDO** |
| Solo SQLite | ✅ | ❌ Limitado | N/A | ❌ No escala |
| Solo PostgreSQL | ⚠️ Setup extra | ✅ | Esquema único | ⚠️ Fricción dev |
| MongoDB | ⚠️ | ⚠️ | Flexible pero desordenado | ❌ Overkill |

**Factores de decisión**:
1. **Experiencia del desarrollador**: SQLite requiere setup cero, perfecto para dev local
2. **Producción**: PostgreSQL probado para cargas de trabajo empresariales
3. **Portabilidad**: Las mismas queries funcionan contra ambas
4. **Licencia**: Ambas open-source, sin costo

**Consecuencias**:
- ✅ Setup cero para desarrolladores
- ✅ Los clientes empresariales obtienen base de datos probada
- ✅ Sin vendor lock-in
- ⚠️ Debe probar migraciones contra ambas
- ⚠️ Algunos dialectos SQL difieren

**Mitigación**:
- Estandarizar en SQL ANSI
- Usar sqlx para queries type-safe
- Testing automatizado contra ambas bases de datos

**RDA relacionadas**: RDA-010 (elección de base de datos vectorial)

---

## RDA-007: Arquitectura local-first (sin nube por defecto)

**Estado**: ✅ **Aceptada**

**Decisión**: ELAP es **capaz de funcionar offline por defecto**. Sin servicios cloud requeridos. Telemetría y actualizaciones permanecen locales.

**Contexto**:
Clientes empresariales (especialmente industrias reguladas) requieren:
- Datos nunca salen del perímetro
- Cumplimiento GDPR, HIPAA, SOC2
- Operación durante interrupciones de internet
- Sin dependencia de infraestructura del vendor

**Alternativas consideradas**:

| Modelo | Offline | Privacidad | Despliegue | Veredicto |
|--------|---------|---------|-----------|---------|
| **Local-first (nube opcional)** | ✅ | ✅ | Hardware del cliente | ✅ **ELEGIDO** |
| Cloud-first (opción self-hosted) | ⚠️ | ⚠️ | Nube + fallback | ❌ No apto |
| Cloud-only | ❌ | ❌ | Servidores del vendor | ❌ Falla SRS |

**Factores de decisión**:
1. **Requisito de mercado**: Industrias reguladas necesitan esto
2. **Diferenciación**: ChatGPT/Claude son cloud-only
3. **Cumplimiento**: GDPR significa datos permanecen en EU, HIPAA significa asegurado
4. **Resiliencia**: Sin internet, ¿aún funciona?

**Consecuencias**:
- ✅ Atractivo para industrias reguladas
- ✅ Sin costos recurrentes de nube para clientes
- ✅ Cumple requisitos de cumplimiento
- ⚠️ Sin logging/monitoreo centralizado (debe ser on-premises)
- ⚠️ Las actualizaciones requieren despliegue manual o VPN

**Mitigación**:
- Proporcionar mecanismo de actualización fácil (binarios firmados)
- Ofrecer sync a nube opcional (para clientes que lo quieran)
- Documentar despliegue en red aislada

**RDA relacionadas**: Ninguna (principio arquitectónico)

---

## RDA-008: RBAC (Control de Acceso Basado en Roles) desde el primer día

**Estado**: ✅ **Aceptada**

**Decisión**: Modelo de seguridad es **RBAC** (Control de Acceso Basado en Roles), ejecutado en nivel del núcleo Rust, no en nivel de aplicación.

**Contexto**:
Despliegue empresarial requiere:
- Permisos granulares (quién puede usar qué agentes/herramientas)
- Pista de auditoría de todas las operaciones
- Prevención de escalada de privilegios
- Cumplimiento de principio de menor privilegio

**Alternativas consideradas**:

| Modelo | Ejecución | Flexibilidad | Implementación |
|--------|-----------|-------------|-----------------|
| **RBAC (núcleo)** | Obligatoria | Roles + reglas | Rust, no se puede bypass | ✅ **ELEGIDO** |
| ACL (Listas de Control de Acceso) | Granular | Usuario por usuario | Difícil de gestionar a escala | ❌ No escalable |
| Límite de confianza (nivel app) | Débil | Alta | Fácil de bypass | ❌ No seguro |

**Factores de decisión**:
1. **Cumplimiento**: Requerido por clientes empresariales
2. **Seguridad**: No puede ocurrir exposición accidental de datos
3. **Auditabilidad**: Los logs muestran quién hizo qué
4. **Escalabilidad**: Los roles son más fáciles de gestionar que ACLs por usuario

**Consecuencias**:
- ✅ Seguridad de nivel empresarial
- ✅ Pistas de auditoría para cumplimiento
- ✅ Previene filtraciones accidentales de datos
- ⚠️ Complejidad de setup inicial (definir roles)
- ⚠️ Costo de rendimiento (checks de permiso en cada operación)

**Mitigación**:
- Cache de checks de permiso
- Documentar plantillas de roles (Ventas, RRHH, TI, etc.)
- Proporcionar UI para gestión de permisos

**RDA relacionadas**: RDA-009 (Cifrado)

---

## RDA-009: Cifrado AES-256 para datos en reposo

**Estado**: ✅ **Aceptada**

**Decisión**: Datos sensibles (configs, secretos, historial de conversación) se cifran con **AES-256** en reposo.

**Contexto**:
Los datos del cliente deben estar protegidos si:
- Hardware robado
- Disco removido
- Acceso no autorizado al sistema de archivos

**Alternativas consideradas**:

| Cifrado | Tamaño clave | Velocidad | Estándar | Veredicto |
|---------|----------|--------|----------|---------|
| **AES-256** | 256-bit | Rápido (aceleración hardware) | FIPS aprobado | ✅ **ELEGIDO** |
| AES-128 | 128-bit | Ligeramente más rápido | FIPS pero más débil | ⚠️ Menos seguro |
| ChaCha20 | 256-bit | Bueno | Estándar IETF | ⚠️ Menos universal |
| Twofish | 256-bit | Más lento | Académico | ❌ Más antiguo |

**Factores de decisión**:
1. **Fortaleza**: La clave de 256-bit resiste ataques cuánticos más tiempo que 128-bit
2. **Rendimiento**: Aceleración hardware disponible (AES-NI)
3. **Estándar**: FIPS 140-2 aprobado
4. **Librería**: La crate Ring tiene implementación battle-tested

**Consecuencias**:
- ✅ Estándar de industria (DoD, NIST aprobado)
- ✅ Protege contra escenarios de robo
- ⚠️ Gestión de claves requerida (¿dónde guardar clave maestra?)
- ⚠️ Costo de rendimiento (mitigado por aceleración hardware)

**Mitigación**:
- Clave guardada solo en memoria (no en disco)
- Derivación de clave desde secreto maestro
- Rotación de clave opcional

**RDA relacionadas**: RDA-007 (Local-first), RDA-008 (RBAC)

---

## RDA-010: Qdrant para producción, ChromaDB para dev

**Estado**: ✅ **Aceptada**

**Decisión**: Base de datos vectorial es **Qdrant** para empresa, **ChromaDB** para desarrollo.

**Contexto**:
RAG (Generación Aumentada por Recuperación) requiere base de datos vectorial:
- Almacenar incrustaciones de documentos
- Búsqueda de similitud semántica
- Escalable a millones de vectores

**Alternativas consideradas**:

| Base de datos | Dev | Empresa | Escrito en | Veredicto |
|-----------|-----|--------|-----------|---------|
| **Qdrant** | ⚠️ Setup extra | ✅ | Rust | ✅ **Empresa** |
| **ChromaDB** | ✅ Fácil | ⚠️ Limitado | Python | ✅ **Dev** |
| Weaviate | ⚠️ | ✅ | Go | ❌ Overkill |
| Pinecone | ⚠️ Cloud-only | ✅ | Managed | ❌ Falla offline |
| Elasticsearch | ⚠️ Complejo | ✅ | Java | ❌ Demasiado pesado |

**Factores de decisión**:
1. **Velocidad de dev**: ChromaDB embebido en proceso, setup cero
2. **Producción**: Qdrant probado, escrito en Rust (ajusta nuestro stack)
3. **Offline**: Ambos se ejecutan localmente (sin dependencia cloud)
4. **Escala**: Qdrant maneja millones de vectores

**Consecuencias**:
- ✅ Transición suave dev → prod
- ✅ Ambos soportan operación offline
- ⚠️ Caminos de configuración diferentes (embebido vs standalone)
- ⚠️ Migración necesaria al pasar de dev a prod

**Mitigación**:
- Abstraer base de datos vectorial detrás de interfaz
- Proporcionar herramientas de migración
- Documentar ambas configuraciones

**RDA relacionadas**: RDA-006 (bases de datos SQL)

---

## RDA-011: Sin fork de código, sistema de plugins en su lugar

**Estado**: ✅ **Aceptada**

**Decisión**: Personalización vía **sistema de plugins**, no forks de código.

**Contexto**:
Los clientes necesitarán personalización (nuevos agentes, herramientas, integraciones). Los forks son insostenibles:
- Merge de upstream difícil
- Cada cliente es un copo de nieve
- Fragmentación de versiones

**Alternativas consideradas**:

| Modelo | Flexibilidad | Mantenibilidad | Ruta de upgrade | Veredicto |
|--------|-------------|-----------------|--------------|---------|
| **Plugins** | Alta | Fácil | Limpio | ✅ **ELEGIDO** |
| Forks | Muy alta | Pesadilla | Doloroso | ❌ Insostenible |
| Solo configuración | Limitada | Fácil | Simple | ⚠️ No lo suficientemente flexible |

**Factores de decisión**:
1. **Escalabilidad**: No puedo mantener N forks
2. **Upgrades**: Los plugins son agnósticos de versión
3. **Ecosistema**: Incentivar contribuciones comunitarias
4. **Negocio**: Oportunidad de marketplace (Fase 6)

**Consecuencias**:
- ✅ Modelo de personalización sostenible
- ✅ Oportunidad de marketplace
- ✅ Ruta de upgrade clara para clientes
- ⚠️ Debe diseñar API de plugin estable
- ⚠️ Carga de seguridad (auditar plugins)

**Mitigación**:
- Definir manifiesto de plugin con permisos
- Aislar plugins (modelo de capacidades)
- Proporcionar SDK y ejemplos
- Proceso de revisión de código para plugins oficiales

**RDA relacionadas**: Ninguna (negocio/arquitectónica)

---

## RDA-012: Conventional Commits para historial git

**Estado**: ✅ **Aceptada**

**Decisión**: Todos los commits siguen especificación **Conventional Commits**.

**Contexto**:
El historial git limpio ayuda:
- Generación de changelog
- Versionado semántico (auto-computar)
- Revisión de código
- Seguridad de revert

**Alternativas consideradas**:

| Formato | Legibilidad | Automatización | Veredicto |
|---------|-------------|-----------|---------|
| **Conventional** | ✅ Claro | ✅ Se puede parsear | ✅ **ELEGIDO** |
| Freeform descriptivo | ✅ Bueno | ❌ No se puede parsear | ❌ Sin automatización |
| Modo imperativo | ✅ Bueno | ❌ Ambiguo | ⚠️ Menos estructura |

**Factores de decisión**:
1. **Automatización**: Se puede generar CHANGELOG
2. **Estándar**: Usado por Angular, Vue, Kubernetes
3. **Claridad**: Tipo + scope + mensaje es preciso

**Consecuencias**:
- ✅ Generación de CHANGELOG automatizada
- ✅ Historial de commits claro
- ✅ Automatización de SemVer posible
- ⚠️ Requiere disciplina (se puede agregar linting)

**Mitigación**:
- Agregar git hooks para ejecutar formato
- Documentar en CLAUDE.md
- Ejemplos en plantillas de PR

**RDA relacionadas**: Ninguna (proceso/herramienta)

---

## Tabla de resumen

| RDA | Decisión | Estado |
|-----|----------|--------|
| 001 | Rust para núcleo | ✅ Aceptada |
| 002 | Python para IA | ✅ Aceptada |
| 003 | gRPC sobre socket | ✅ Aceptada |
| 004 | Tauri desktop | ✅ Aceptada |
| 005 | Tokio async | ✅ Aceptada |
| 006 | SQLite+PostgreSQL | ✅ Aceptada |
| 007 | Local-first | ✅ Aceptada |
| 008 | Seguridad RBAC | ✅ Aceptada |
| 009 | Cifrado AES-256 | ✅ Aceptada |
| 010 | Qdrant+ChromaDB vectores | ✅ Aceptada |
| 011 | Plugins > forks | ✅ Aceptada |
| 012 | Conventional Commits | ✅ Aceptada |

---

**Versión del documento**: 1.0-alpha  
**Última actualización**: 2026-08-04  
**Próxima revisión**: Después de Fase 1, actualizar con RDAs de Fase 1
