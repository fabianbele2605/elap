# Contributing to ELAP

**ELAP** es un proyecto open-source empresarial. Bienvenido, contribuyente.

## Cómo empezar

### 1. Fork y clon
```bash
git clone https://github.com/tu-usuario/elap.git
cd elap
```

### 2. Setup local

**Requisitos:**
- Rust 1.89+ (`rustup update`)
- Python 3.12+ (`python --version`)
- Node.js 18+ (`node --version`)
- Docker (opcional, para gRPC)

**Setup:**
```bash
# Rust core
cd crates/elap-core
cargo build --release

# Python AI Runtime
cd python
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o: venv\Scripts\activate  (Windows)
pip install -r requirements.txt

# Web frontend
cd web
npm install
npm run dev
```

### 3. Branch naming

```
feature/core-engine           # Nueva funcionalidad
fix/security-rbac             # Bug fix
docs/api-documentation        # Documentación
refactor/streaming-handler    # Refactoring
test/integration-tests        # Tests

NUNCA: main, master, dev (estas son protegidas)
```

### 4. Commits

**Formato (OBLIGATORIO en ESPAÑOL):**
```
tipo(scope): Mensaje corto

Párrafo explicativo que describe QUÉ y POR QUÉ.
No describas CÓMO (eso es el código).

Fixes #123
Breaking change: ...
```

**Tipos válidos:**
- `feat` - Nueva funcionalidad
- `fix` - Bug fix
- `docs` - Documentación
- `test` - Tests o coverage
- `refactor` - Cambio interno
- `ci` - CI/CD changes
- `chore` - Deps, build, etc.

**Ejemplo:**
```
feat(agent): Agregar orquestador multi-agente

Implementa sistema de delegación automática.
Los agentes se asignan según palabras clave en query.

Fixes #42
```

## Cómo contribuir

### Reportar bugs

**GitHub Issues:**
1. Click "New Issue"
2. Selecciona template "Bug Report"
3. Describe: qué pasó, qué esperabas, pasos para reproducir
4. Incluye: versión, OS, logs

**NO hacer:**
- Abrir issue para preguntas (usa Discussions)
- Duplicar issues existentes
- Incluir contraseñas, keys, tokens

### Proponer features

**GitHub Discussions:**
1. Abre una discusión en "Ideas"
2. Describe el problema que resuelve
3. Propón solución
4. Espera feedback

**Si gusta:**
- Alguien abre issue oficial
- Puedes hacer PR

### Submit PR

**Checklist antes de PR:**

```
[ ] Código compila sin warnings
[ ] Tests pasan (cargo test, pytest)
[ ] Coverage > 80% (Rust), > 75% (Python)
[ ] Documentación actualizada
[ ] Commit message sigue formato
[ ] No hay merge conflicts
[ ] No incluye secrets
```

**Paso a paso:**

1. **Crea branch:**
   ```bash
   git checkout -b feature/tu-feature
   ```

2. **Haz cambios:**
   - Edita código
   - Añade tests
   - Actualiza docs

3. **Verifica:**
   ```bash
   # Rust
   cargo fmt
   cargo clippy
   cargo test

   # Python
   black python/
   ruff check python/
   pytest

   # Web
   npm run lint
   npm run build
   ```

4. **Commit:**
   ```bash
   git add archivo1 archivo2
   git commit -m "feat(scope): Mensaje"
   ```

5. **Push:**
   ```bash
   git push origin feature/tu-feature
   ```

6. **PR en GitHub:**
   - Título < 70 caracteres
   - Descripción: qué, por qué, cómo testear
   - Link a issues: `Fixes #123`
   - Espera review

## Standards de código

### Rust
```rust
// ✅ Correcto
// Nombres claros, types explícitos
pub fn validate_permissions(user_id: &str, resource: &str) -> Result<bool> {
    // Máximo 100 líneas por función
    // Usa ? operator, no unwrap()
    let config = load_config()?;
    Ok(config.has_permission(user_id, resource))
}

// ❌ Evitar
pub fn vp(u: &str, r: &str) -> Result<bool> {  // Nombres cortos
    load_config().unwrap()  // unwrap()!
}
```

### Python
```python
# ✅ Correcto
from typing import Optional
import asyncio

async def process_query(user_id: str, query: str) -> dict:
    """Process user query."""
    result = await execute(query)
    return {"status": "ok", "result": result}

# ❌ Evitar
def process(u, q):  # Sin type hints
    print(result)  # print() en production!
```

### Tests
```rust
#[test]
fn test_permission_validation_success() {
    // Arrange
    let rbac = RbacManager::new();
    
    // Act
    let result = rbac.validate_permission("user_123", "read_data");
    
    // Assert
    assert!(result.is_ok());
}
```

## Review process

### Para mantenedores:

1. **Code Review:**
   - ¿Compila?
   - ¿Tests pasan?
   - ¿Sigue standards?
   - ¿Documentado?

2. **Aprobar:**
   - ✅ Si todo está bien
   - Merge con "Squash and merge"

3. **Rechazar:**
   - Request changes
   - Explica por qué
   - Propón alternativas

### Para autores:

1. Responde feedback
2. Pushea cambios
3. Espera re-review
4. Si se aprueba → merge automático

## Desarrollo

### Estructura
```
crates/
├── elap-core/        # Rust core
│   ├── src/
│   └── tests/
├── elap-cli/
└── elap-desktop/

python/
├── src/elap_ai/
├── tests/
└── requirements.txt

web/
├── src/
└── package.json
```

### Build local
```bash
# Rust
cargo build --release
cargo test
cargo clippy

# Python
pytest --cov=elap_ai

# Web
npm run build
npm run test
```

### Docs obligatorias
```
[ ] Code comments (solo WHY, no WHAT)
[ ] Function docstrings
[ ] README actualizado
[ ] CHANGELOG.md entry
```

## Support

- **Preguntas**: GitHub Discussions
- **Bugs**: GitHub Issues
- **Security**: security@bblabs.io
- **Contacto**: hello@bblabs.io

## Licencia

ELAP es MIT licensed. Al contribuir, aceptas esta licencia.

---

**¡Gracias por mejorar ELAP! 🚀**

Última actualización: 2026-08-06
