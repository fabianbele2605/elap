# Plataforma Enterprise Local de IA (ELAP)

**Versión:** 0.1.0  
**Estado:** Fase 0 — Inicialización  
**Última actualización:** 2026-08-04

---

## 🎯 ¿Qué es ELAP?

ELAP es una plataforma de IA local, 100% offline-first, para empresas que necesitan:

- **Privacidad absoluta**: Ningún dato sale de tu infraestructura
- **Costo predecible**: Sin pagos por token
- **Especialización por rol**: Agentes preconfigurados para cada departamento
- **Operación offline**: Funciona completamente sin internet
- **Control total**: Auditoría completa y RBAC granular

---

## 📁 Estructura del proyecto

```
elap/
├── crates/              # Núcleo Rust (Motor, Escritorio, CLI)
├── python/              # Motor de IA (Python)
├── docs/                # Documentación técnica
├── notebook/            # Libros para NotebookLM (material de estudio)
├── tooling/             # Scripts, CI/CD, Docker
└── .github/             # Flujos de trabajo de GitHub Actions
```

---

## 🚀 Inicio rápido

### Requisitos previos

- **Rust**: 1.75+
- **Python**: 3.11+
- **Git**: 2.0+

### Instalación local (desarrollo)

```bash
# Clonar y entrar
git clone https://github.com/bblabs/elap.git
cd elap

# Compilar Rust
cargo build

# Instalar dependencias Python
cd python
pip install -e .
cd ..

# Ejecutar tests
cargo test
python -m pytest

# Ejecutar core
cargo run --bin elap-cli help
```

---

## 📚 Documentación

### Para desarrolladores
- **[CLAUDE.md](CLAUDE.md)** — Estándares de código, patrones, convenciones
- **[docs/01-Architecture/](docs/01-Architecture/)** — Arquitectura detallada
- **[docs/02-Development/](docs/02-Development/)** — Guía de desarrollo local
- **[docs/03-Modules/](docs/03-Modules/)** — Documentación de cada módulo

### Para aprender
- **[notebook/Libro-01-Introduccion/](notebook/Libro-01-Introduccion/)** — Introducción (didáctica)
- **[notebook/Libro-02-Core-Runtime/](notebook/Libro-02-Core-Runtime/)** — Core Runtime
- **[notebook/Libro-03-Desktop-Runtime/](notebook/Libro-03-Desktop-Runtime/)** — Desktop
- ... (18 libros en total)

### Documentación técnica publicada
- **[ROADMAP.md](docs/00-Project/ROADMAP.md)** — Fases 0-17
- **[CHANGELOG.md](docs/00-Project/CHANGELOG.md)** — Cambios por versión
- **[TODO.md](docs/00-Project/TODO.md)** — Pendientes actuales

---

## 🏗️ Fases del proyecto

| Fase | Nombre | Estado | Inicio estimado |
|------|--------|--------|-----------------|
| 0 | Fundacionales | 🔄 En progreso | Semana 1 |
| 1 | Motor Central | ⏳ Por hacer | Semana 2 |
| 2 | Motor de Escritorio | ⏳ Por hacer | Semana 3 |
| 3 | Gestor de Configuración | ⏳ Por hacer | Semana 4 |
| 4 | Logging | ⏳ Por hacer | Semana 5 |
| 5 | Manejo de Errores | ⏳ Por hacer | Semana 6 |
| 6 | Motor de Plugins | ⏳ Por hacer | Semana 7 |
| 7 | Motor de Herramientas | ⏳ Por hacer | Semana 8 |
| 8 | Gestor de Modelos | ⏳ Por hacer | Semana 9 |
| 9 | Motor de IA Python | ⏳ Por hacer | Semana 10 |
| 10 | Gestor de Memoria | ⏳ Por hacer | Semana 11 |
| 11 | Motor de Flujos | ⏳ Por hacer | Semana 12 |
| 12 | Motor de Agentes | ⏳ Por hacer | Semana 13 |
| 13 | Interfaz Gráfica | ⏳ Por hacer | Semana 14 |
| 14 | Instalador | ⏳ Por hacer | Semana 15 |
| 15 | Actualizador | ⏳ Por hacer | Semana 16 |
| 16 | Testing | ⏳ Por hacer | Semana 17 |
| 17 | Empaquetado | ⏳ Por hacer | Semana 18 |

Ver [ROADMAP.md](docs/00-Project/ROADMAP.md) para detalles.

---

## 💻 Stack tecnológico

| Componente | Lenguaje | Tecnologías |
|-----------|----------|-------------|
| **Motor Central** | Rust | Tokio, Tonic (gRPC), Tauri |
| **CLI** | Rust | Clap, Tracing |
| **Interfaz Gráfica** | Rust/TypeScript | Tauri, React/Vue |
| **Motor de IA** | Python | LangGraph, Transformers, Ollama |
| **Base de datos** | SQL | PostgreSQL, SQLite |
| **Base de datos vectorial** | Vector | Qdrant, ChromaDB |
| **Seguridad** | Rust | Ring, AES-256, RBAC |

---

## 🤝 Cómo contribuir

Este proyecto está en construcción bajo un enfoque **Documentación Viva**:

1. **Código** siempre viene acompañado de documentación técnica
2. **Cada fase** genera documentos para desarrolladores y material de estudio
3. **NotebookLM** es nuestro material de transferencia de conocimiento

Si contribuyes, asegúrate de:
- Leer [CLAUDE.md](CLAUDE.md) para convenciones
- Generar documentación junto al código
- Actualizar [CHANGELOG.md](docs/00-Project/CHANGELOG.md)
- Crear/actualizar capítulos en [notebook/](notebook/)

---

## 📖 Libros para estudiar (NotebookLM)

Cuando el proyecto esté completo, tendrás 18 libros completos:

1. Introducción a ELAP
2. Motor Central
3. Motor de Escritorio
4. Gestor de Configuración
5. Logging
6. Manejo de Errores
7. Motor de Plugins
8. Motor de Herramientas
9. Gestor de Modelos
10. Motor de IA
11. Gestor de Memoria
12. Motor de Flujos
13. Motor de Agentes
14. Instalador
15. Despliegue
16. Testing
17. CI/CD
18. Guía de Administración Empresarial

Todos didácticos, con ejemplos, analogías, preguntas frecuentes y glosario.

---

## 📄 Licencia

Este proyecto es software propietario de BBLABS. Todos los derechos reservados.

---

## 📞 Contacto

- **Email**: fabian.beleno@bblabs.io
- **Organización**: BBLABS
- **Documentación**: Ver [docs/](docs/) y [notebook/](notebook/)

---

## ✅ Checklist de estado (Fase 0)

- [x] Git inicializado
- [x] Estructura de carpetas creada
- [x] `.gitignore` configurado
- [ ] `CLAUDE.md` completado
- [ ] `Cargo.toml` (workspace) creado
- [ ] `pyproject.toml` creado
- [ ] Crates Rust inicializados
- [ ] Python package inicializado
- [ ] Documentación fundacional completada
- [ ] Primer commit realizado

---

**Siguiente**: [CLAUDE.md](CLAUDE.md) — Estándares y convenciones del proyecto.
