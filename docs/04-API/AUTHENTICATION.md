# Autenticación JWT + RBAC — Seguridad de API

**Autor**: ELAP Development Team  
**Fecha**: 2026-08-05  
**Versión**: 1.0  
**Fase**: 10

## Índice

1. [Descripción General](#descripción-general)
2. [Flujo de Autenticación](#flujo-de-autenticación)
3. [Roles y Permisos](#roles-y-permisos)
4. [Endpoints](#endpoints)
5. [Ejemplos](#ejemplos)

---

## Descripción General

La API implementa:
- **JWT (JSON Web Tokens)** para autenticación sin sesiones
- **RBAC (Role-Based Access Control)** para autorización
- **Claims validados** con expiración de 24 horas
- **3 roles predefinidos** con permisos jerárquicos

### Características

- ✅ **Sin estado** - JWT no requiere servidor de sesiones
- ✅ **Escalable** - Múltiples instancias pueden validar tokens
- ✅ **Seguro** - Tokens firmados con HMAC-SHA256
- ✅ **Flexible** - RBAC personalizable por rol

---

## Flujo de Autenticación

```
┌─────────────────────────────────────┐
│  1. Cliente solicita login          │
│     POST /login                     │
│     { "usuario": "john",            │
│       "contraseña": "password" }    │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│  2. Servidor valida credenciales    │
│     (en BD, LDAP, etc)              │
│     Asigna rol según usuario        │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│  3. Genera JWT token                │
│     Claims:                         │
│     - sub: usuario                  │
│     - rol: Admin/User/Guest         │
│     - exp: +24h                     │
│     - iat: ahora                    │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│  4. Retorna token al cliente        │
│     { "token": "eyJhbGc..." }       │
└─────────────────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│  5. Cliente usa token en headers    │
│     GET /agents                     │
│     Authorization: Bearer [token]   │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│  6. Servidor valida token           │
│     - Verifica firma                │
│     - Valida expiración             │
│     - Extrae claims                 │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│  7. Valida permiso (RBAC)           │
│     ¿Rol tiene permiso para acción? │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│  8. Ejecuta endpoint                │
│     200 OK si permitido             │
│     403 Forbidden si denegado       │
└─────────────────────────────────────┘
```

---

## Roles y Permisos

### Admin

```json
{
  "rol": "Admin",
  "permisos": ["crear", "leer", "actualizar", "eliminar", "ejecutar"]
}
```

- ✅ Crear agentes
- ✅ Leer todo
- ✅ Actualizar agentes
- ✅ Eliminar agentes
- ✅ Ejecutar agentes

### User

```json
{
  "rol": "User",
  "permisos": ["crear", "leer", "actualizar", "ejecutar"]
}
```

- ✅ Crear agentes propios
- ✅ Leer agentes accesibles
- ✅ Actualizar agentes propios
- ❌ Eliminar agentes
- ✅ Ejecutar agentes propios

### Guest

```json
{
  "rol": "Guest",
  "permisos": ["leer"]
}
```

- ❌ Crear agentes
- ✅ Leer agentes públicos
- ❌ Actualizar agentes
- ❌ Eliminar agentes
- ❌ Ejecutar agentes

---

## Endpoints

### 1. POST /login — Obtener Token

**Request**:
```json
{
  "usuario": "john_doe",
  "contraseña": "securepassword123"
}
```

**Response** (200 OK):
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "usuario": "john_doe",
  "rol": "User"
}
```

**Errores**:
- `400 Bad Request` - Usuario o contraseña vacíos
- `401 Unauthorized` - Credenciales inválidas (future)

---

### 2. Headers Requeridos

Todos los endpoints (excepto `/login`) requieren:

```
Authorization: Bearer <token>
```

**Ejemplo**:
```bash
curl -H "Authorization: Bearer eyJhbGc..." \
     http://localhost:3000/agents
```

---

## Ejemplos

### Ejemplo 1: Flow Completo en cURL

```bash
# 1. Login
TOKEN=$(curl -X POST http://localhost:3000/login \
  -H "Content-Type: application/json" \
  -d '{
    "usuario": "admin",
    "contraseña": "admin123"
  }' | jq -r '.token')

echo "Token: $TOKEN"

# 2. Usar token en request
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:3000/agents

# 3. Crear agente (requiere Admin o User)
curl -X POST http://localhost:3000/agents \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Analizador",
    "rol": "Data Scientist",
    "objetivo": "Procesar datos"
  }'
```

### Ejemplo 2: JavaScript con Fetch

```javascript
// Paso 1: Login
const loginResponse = await fetch('http://localhost:3000/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    usuario: 'john_doe',
    contraseña: 'password123'
  })
});

const { token } = await loginResponse.json();
console.log('Token obtenido:', token);

// Paso 2: Usar token
const agentsResponse = await fetch('http://localhost:3000/agents', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const agents = await agentsResponse.json();
console.log('Agentes:', agents);

// Paso 3: Crear agente
const createResponse = await fetch('http://localhost:3000/agents', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    nombre: 'Bot Vendedor',
    rol: 'Sales',
    objetivo: 'Procesar pedidos'
  })
});

if (createResponse.status === 403) {
  console.error('Permiso denegado - verificar rol');
} else {
  const agent = await createResponse.json();
  console.log('Agente creado:', agent);
}
```

### Ejemplo 3: Rust Client

```rust
use reqwest;
use serde::{Deserialize, Serialize};

#[derive(Serialize)]
struct LoginRequest {
    usuario: String,
    contraseña: String,
}

#[derive(Deserialize)]
struct LoginResponse {
    token: String,
}

#[tokio::main]
async fn main() {
    let client = reqwest::Client::new();

    // Login
    let login_resp = client
        .post("http://localhost:3000/login")
        .json(&LoginRequest {
            usuario: "user".to_string(),
            contraseña: "pass".to_string(),
        })
        .send()
        .await
        .unwrap();

    let LoginResponse { token } = login_resp.json().await.unwrap();

    // Usar token
    let agents = client
        .get("http://localhost:3000/agents")
        .header("Authorization", format!("Bearer {}", token))
        .send()
        .await
        .unwrap()
        .json()
        .await
        .unwrap();

    println!("Agentes: {:?}", agents);
}
```

---

## Detalles Técnicos

### Token JWT

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
eyJzdWIiOiJ1c2VyMTIzIiwicm9sIjoiVXNlciIsImV4cCI6MTY5MTEyMzQ1NiwiaWF0IjoxNjkwMTIzNDU2fQ.
abcdef123456...
```

**Header**: Algoritmo HMAC-SHA256
**Payload (Claims)**:
```json
{
  "sub": "usuario123",
  "rol": "User",
  "exp": 1691123456,
  "iat": 1690123456
}
```

### Validación

1. ✅ Verificar firma con secret key
2. ✅ Validar timestamp de expiración
3. ✅ Extraer claims (sub, rol)
4. ✅ Verificar RBAC para acción

### Duración de Token

- **Validez**: 24 horas
- **Refresh**: Implementado en Fase 11 (future)
- **Revocación**: Implementado en Fase 11 (future)

---

## Mejores Prácticas

### ✅ Hacer

```bash
# Almacenar token seguro en cliente
localStorage.setItem('jwt_token', token);

# Enviar en header
Authorization: Bearer <token>

# Usar HTTPS en producción
https://api.example.com/agents
```

### ❌ No Hacer

```bash
# ❌ Enviar token en URL
GET /agents?token=eyJ...

# ❌ Guardar token en cookies sin httpOnly
document.cookie = 'token=' + jwt;

# ❌ Usar HTTP en producción
http://api.example.com/agents
```

---

## Próximas Fases

- **Fase 11**: Token refresh y revocation
- **Fase 11**: OAuth2 integration
- **Fase 12**: MFA (Multi-Factor Authentication)

---

**Última actualización**: 2026-08-05
