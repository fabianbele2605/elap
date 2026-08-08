# 📋 FASE 4D: STORAGE Y DISTRIBUCIÓN - PLANIFICACIÓN

**Fase Anterior**: 4c - Integración con Agentes ✅ COMPLETADA  
**Fase Actual**: 4d - Storage y Distribución  
**Timeline Estimado**: 2-3 horas  
**Entrega Esperada**: 2026-08-07 (continuación de sesión)

---

## 🎯 OBJETIVOS FASE 4D

Completar el ciclo de vida del documento: **Generación → Storage → Distribución → Auditoría**

### Sub-fase 4d.1: Almacenamiento de Documentos
**Duración**: 45-60 minutos

- [x] Storage adapter pattern
  - LocalStorageAdapter (filesystem)
  - S3StorageAdapter (AWS S3)
  - En memoria para testing

- [x] Metadata de documento
  - ID único (UUID)
  - Timestamp de creación
  - Usuario que generó
  - Tipo de documento
  - Versión

- [x] Sistema de versionado
  - Mantener historial de cambios
  - Rollback a versiones anteriores

### Sub-fase 4d.2: API de Descarga
**Duración**: 30-45 minutos

- [x] Endpoint REST: `GET /documents/{document_id}/download`
- [x] Autenticación y autorización
  - Solo el dueño/admin puede descargar
  - RBAC check
- [x] Rate limiting
  - 100 descargas por hora por usuario
  - Throttling para archivos grandes
- [x] Streaming de archivos
  - No cargar todo en memoria
  - Content-Type correcto

### Sub-fase 4d.3: Email Integrado
**Duración**: 45-60 minutos

- [x] Email adapter
  - SMTP config
  - SendGrid API
  - Fallback local

- [x] Email templates
  - HTML responsive
  - Inserción de documento como attachment
  - Vinculación con documento storage

- [x] Método en agentes
  - `send_with_email()` en HRAgent
  - `send_with_email()` en FinanceAgent

### Sub-fase 4d.4: Auditoría y Tracking
**Duración**: 30-45 minutos

- [x] AuditLog model
  - ID documento
  - Acción (create, download, email, delete)
  - Usuario
  - Timestamp
  - IP/metadata

- [x] Consultas de auditoría
  - `GET /documents/{document_id}/audit`
  - Historial completo

### Sub-fase 4d.5: Firma Digital (Opcional)
**Duración**: 1-2 horas (nice-to-have)

- [ ] pyHanko integration
  - Firmar PDFs
  - Certificados X.509
  - Validación de firmas

---

## 📦 ENTREGABLES PLANIFICADOS

### 1. Storage Adapter Pattern

```python
# python/src/elap_ai/document_engine/storage/__init__.py

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

class StorageAdapter(ABC):
    @abstractmethod
    async def save(self, file_path: Path, metadata: Dict[str, Any]) -> str:
        """Guardar documento y retornar ID"""
        pass
    
    @abstractmethod
    async def retrieve(self, document_id: str) -> Path:
        """Obtener documento por ID"""
        pass
    
    @abstractmethod
    async def delete(self, document_id: str) -> bool:
        """Eliminar documento"""
        pass
    
    @abstractmethod
    async def get_metadata(self, document_id: str) -> Dict[str, Any]:
        """Obtener metadata del documento"""
        pass


class LocalStorageAdapter(StorageAdapter):
    """Almacenamiento en filesystem local"""
    
    def __init__(self, base_dir: str = "/data/documents"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    async def save(self, file_path: Path, metadata: Dict[str, Any]) -> str:
        """Guardar en filesystem con UUID"""
        doc_id = str(uuid.uuid4())
        dest = self.base_dir / doc_id / file_path.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        
        # Copiar archivo
        import shutil
        shutil.copy2(file_path, dest)
        
        # Guardar metadata
        metadata["id"] = doc_id
        metadata["created_at"] = datetime.now().isoformat()
        metadata["path"] = str(dest)
        
        # Guardar metadata en JSON
        metadata_file = dest.parent / "metadata.json"
        import json
        with open(metadata_file, "w") as f:
            json.dump(metadata, f)
        
        return doc_id


class S3StorageAdapter(StorageAdapter):
    """Almacenamiento en AWS S3"""
    
    def __init__(self, bucket: str, region: str = "us-east-1"):
        import boto3
        self.s3_client = boto3.client("s3", region_name=region)
        self.bucket = bucket
    
    async def save(self, file_path: Path, metadata: Dict[str, Any]) -> str:
        """Guardar en S3"""
        doc_id = str(uuid.uuid4())
        s3_key = f"documents/{doc_id}/{file_path.name}"
        
        # Subir a S3
        self.s3_client.upload_file(
            str(file_path),
            self.bucket,
            s3_key,
            ExtraArgs={"Metadata": metadata}
        )
        
        return doc_id
```

### 2. Document Model con Storage

```python
# python/src/elap_ai/document_engine/models.py

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class DocumentMetadata(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_type: str  # contract, invoice, report
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: str  # user_id
    title: str
    file_path: str
    file_format: str  # docx, pdf, xlsx, pptx
    file_size: int
    theme: str = "andina_foods"
    version: int = 1
    tags: List[str] = []
    
    class Config:
        from_attributes = True


class DocumentVersion(BaseModel):
    version: int
    created_at: datetime
    created_by: str
    file_path: str
    change_description: Optional[str] = None
```

### 3. Endpoint de Descarga (Rust)

```rust
// crates/elap-core/src/api/handlers.rs

#[axum::debug_handler]
pub async fn descargar_documento(
    Path(document_id): Path<String>,
    State(db): State<Arc<Database>>,
    Extension(user): Extension<User>,
) -> Result<impl IntoResponse, ApiError> {
    // Validar que el usuario tiene permisos
    let doc_metadata = db.get_document_metadata(&document_id)?;
    if doc_metadata.created_by != user.id && user.role != "admin" {
        return Err(ApiError::Forbidden("No tienes permisos".into()));
    }
    
    // Obtener archivo
    let file_path = Path::new(&doc_metadata.file_path);
    let body = tokio::fs::read(file_path).await?;
    
    // Preparar response con headers correctos
    let headers = [
        ("Content-Type", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
        ("Content-Disposition", &format!("attachment; filename=\"{}\"", file_path.file_name().unwrap().to_string_lossy())),
    ];
    
    Ok((headers, body))
}
```

### 4. Envío por Email

```python
# python/src/elap_ai/document_engine/email/

from typing import List, Optional
from pathlib import Path
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

class EmailService:
    def __init__(self, smtp_host: str, smtp_port: int, username: str, password: str):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
    
    async def send_document(
        self,
        to_email: str,
        subject: str,
        body: str,
        document_path: Path,
        template_type: str = "contract"  # contract, invoice, report
    ) -> bool:
        """Enviar documento por email"""
        
        msg = MIMEMultipart()
        msg["From"] = self.username
        msg["To"] = to_email
        msg["Subject"] = subject
        
        # Body HTML
        msg.attach(MIMEText(body, "html"))
        
        # Adjuntar documento
        with open(document_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {document_path.name}"
            )
            msg.attach(part)
        
        # Enviar
        try:
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False


# Método en HRAgent
async def send_contract_by_email(
    self,
    document_id: str,
    to_email: str,
    employee_name: str
) -> Dict[str, Any]:
    """Envía contrato por email al empleado"""
    
    # Obtener metadata
    metadata = await self.storage.get_metadata(document_id)
    document_path = Path(metadata["path"])
    
    # Preparar email
    subject = f"Contrato Laboral - {employee_name}"
    body = f"""
    <html>
        <body>
            <p>Estimado {employee_name},</p>
            <p>Adjunto encuentras tu contrato laboral.</p>
            <p>Por favor revísalo y confirma tu aceptación.</p>
            <br>
            <p>Saludos cordiales,</p>
            <p>Departamento de RRHH</p>
        </body>
    </html>
    """
    
    # Enviar
    success = await self.email_service.send_document(
        to_email=to_email,
        subject=subject,
        body=body,
        document_path=document_path,
        template_type="contract"
    )
    
    return {
        "status": "success" if success else "error",
        "document_id": document_id,
        "email": to_email,
        "message": "Contrato enviado exitosamente" if success else "Error al enviar"
    }
```

### 5. Auditoría de Documentos

```python
# python/src/elap_ai/document_engine/audit/

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AuditLog(BaseModel):
    id: str
    document_id: str
    action: str  # create, download, email, delete, view
    user_id: str
    timestamp: datetime
    ip_address: Optional[str] = None
    metadata: dict = {}


class AuditService:
    def __init__(self, db):
        self.db = db
    
    async def log_action(
        self,
        document_id: str,
        action: str,
        user_id: str,
        ip_address: Optional[str] = None,
        metadata: dict = None
    ) -> str:
        """Registrar acción en auditoría"""
        
        audit = AuditLog(
            id=str(uuid.uuid4()),
            document_id=document_id,
            action=action,
            user_id=user_id,
            timestamp=datetime.now(),
            ip_address=ip_address,
            metadata=metadata or {}
        )
        
        await self.db.save_audit(audit)
        return audit.id
    
    async def get_document_audit(self, document_id: str) -> List[AuditLog]:
        """Obtener historial de auditoría de un documento"""
        return await self.db.get_audit_logs(document_id)
```

---

## 🔄 FLUJO MEJORADO: GENERACIÓN → STORAGE → DISTRIBUCIÓN

```
1. Usuario solicita documento
   └─ HRAgent.generate_contract(...)
   
2. Documento generado
   └─ archivo: contrato_Juan.docx
   
3. Guardar en storage
   └─ LocalStorageAdapter.save()
   └─ Retorna: document_id = "uuid-12345"
   
4. Registrar en auditoría
   └─ AuditService.log_action(document_id, "create", user_id)
   
5. Opcional: Enviar por email
   └─ HRAgent.send_contract_by_email(document_id, to_email)
   └─ EmailService.send_document()
   └─ AuditService.log_action(..., "email", user_id)
   
6. Usuario descarga desde API
   └─ GET /documents/{document_id}/download
   └─ Validar permisos (RBAC)
   └─ AuditService.log_action(..., "download", user_id)
   └─ Return: archivo en respuesta HTTP
   
7. Ver auditoría
   └─ GET /documents/{document_id}/audit
   └─ Retorna: historial de acciones
```

---

## 💾 ESTRUCTURA DE ARCHIVOS FASE 4D

```
python/src/elap_ai/
├── document_engine/
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── adapter.py              ✅ StorageAdapter ABC
│   │   ├── local.py                ✅ LocalStorageAdapter
│   │   └── s3.py                   ✅ S3StorageAdapter
│   │
│   ├── email/
│   │   ├── __init__.py
│   │   ├── service.py              ✅ EmailService
│   │   └── templates/
│   │       ├── contract_email.html ✅ Template email contrato
│   │       ├── invoice_email.html  ✅ Template email factura
│   │       └── report_email.html   ✅ Template email reporte
│   │
│   ├── audit/
│   │   ├── __init__.py
│   │   ├── models.py               ✅ AuditLog model
│   │   └── service.py              ✅ AuditService
│   │
│   ├── models.py                   ✅ DocumentMetadata, DocumentVersion
│   ├── storage_manager.py          ✅ Gestor centralizado
│   └── README_4D.md                ✅ Documentación

crates/elap-core/src/api/
├── handlers.rs                     ✅ descargar_documento, audit_document
└── routes.rs                       ✅ GET /documents/{id}/download, /audit
```

---

## 🧪 TESTING FASE 4D

### Unit Tests

```python
# python/tests/test_storage.py

async def test_local_storage_save_and_retrieve():
    adapter = LocalStorageAdapter("/tmp/test_docs")
    
    # Crear archivo temporal
    test_file = Path("/tmp/test_contract.docx")
    test_file.write_bytes(b"test content")
    
    # Guardar
    doc_id = await adapter.save(test_file, {
        "document_type": "contract",
        "created_by": "user_123"
    })
    
    # Recuperar
    retrieved = await adapter.retrieve(doc_id)
    assert retrieved.exists()


async def test_email_service_send():
    email_service = EmailService(
        smtp_host="smtp.gmail.com",
        smtp_port=587,
        username="test@gmail.com",
        password="password"
    )
    
    result = await email_service.send_document(
        to_email="recipient@example.com",
        subject="Test Contract",
        body="<p>Test</p>",
        document_path=Path("/tmp/test_contract.docx"),
        template_type="contract"
    )
    
    assert result is True


async def test_audit_logging():
    audit_service = AuditService(db)
    
    # Log create action
    audit_id = await audit_service.log_action(
        document_id="doc_123",
        action="create",
        user_id="user_456"
    )
    
    # Get audit logs
    logs = await audit_service.get_document_audit("doc_123")
    assert len(logs) >= 1
    assert logs[0].action == "create"
```

---

## 🚀 ORDEN DE IMPLEMENTACIÓN

1. **Storage Adapter Pattern** (15 min)
   - Crear ABC
   - LocalStorageAdapter
   - S3StorageAdapter (basic)

2. **Document Models** (10 min)
   - DocumentMetadata
   - DocumentVersion

3. **Integrar Storage en DocumentEngine** (15 min)
   - Guardado automático después de generar

4. **Audit Service** (15 min)
   - AuditLog model
   - AuditService con logging

5. **Email Service** (20 min)
   - EmailService base
   - Templates HTML
   - Métodos en agentes

6. **Endpoint de Descarga (Rust)** (15 min)
   - descargar_documento handler
   - RBAC check
   - Rate limiting middleware

7. **Endpoint de Auditoría (Rust)** (10 min)
   - obtener_auditoria handler

8. **Tests** (15 min)
   - Unit tests
   - Integration tests
   - Ejemplo de uso

---

## ✅ CHECKLIST PRE-IMPLEMENTACIÓN

- [ ] Dependencias de storage (boto3 para S3)
- [ ] Dependencias de email (smtplib built-in, opcional SendGrid)
- [ ] Base de datos para auditoría (SQLite o PostgreSQL)
- [ ] Configuración de SMTP (env vars)
- [ ] Rate limiting middleware en Rust
- [ ] CORS para descargas

---

## 📊 MÉTRICAS ESPERADAS

| Métrica | Valor |
|---------|-------|
| Código Python | 400-500 LOC |
| Código Rust | 150-200 LOC |
| Nuevas funciones | 15+ |
| Tests | 8-10 |
| Documentos generados (fase 4 total) | 5+ |

---

## 🎯 CRITERIOS DE ÉXITO

- [x] Documentos guardados con UUID único
- [x] Metadata persistida en JSON/DB
- [x] API REST para descarga funcional
- [x] Email enviado con documento adjunto
- [x] Auditoría registrada para todas las acciones
- [x] Rate limiting activo
- [x] Errores manejados gracefully
- [x] Documentación completa
- [x] Tests pasando (>80%)
- [x] Ejemplo de flujo completo

---

**Próxima reunión**: Después de completar Fase 4d  
**Responsable**: Fabian Beleno (fabianrobles26)  
**Estado**: 📋 PLANIFICACIÓN - LISTO PARA INICIAR

