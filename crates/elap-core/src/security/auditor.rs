use std::time::SystemTime;
use std::sync::Mutex;

/// Registro de una acción auditada en el sistema.
#[derive(Debug, Clone)]
pub struct RegistroAuditoria {
    /// ID del usuario que realizó la acción.
    pub usuario_id: String,
    /// Acción realizada (ej: "ejecutar_herramienta").
    pub accion: String,
    /// Recurso sobre el cual se actuó.
    pub recurso: String,
    /// Resultado: "exitoso" o "denegado".
    pub resultado: String,
    /// Timestamp Unix cuando ocurrió.
    pub timestamp: u64,
}

impl RegistroAuditoria {
    /// Crea un nuevo registro de auditoria.
    pub fn nuevo(usuario_id: String, accion: String, recurso: String, resultado: String) -> Self {
        let timestamp = SystemTime::now()
            .duration_since(SystemTime::UNIX_EPOCH)
            .unwrap()
            .as_secs();

        Self {
            usuario_id,
            accion,
            recurso,
            resultado,
            timestamp,
        }
    }
}

/// Auditor de acceso para ELAP.
/// Registra quién hizo qué, cuándo, y si fue permitido.
#[derive(Debug)]
pub struct AuditorRbac {
    /// Lista de registros auditados.
    registros: Mutex<Vec<RegistroAuditoria>>,
}

impl AuditorRbac {
    /// Crea un nuevo auditor.
    pub fn nuevo() -> Self {
        Self {
            registros: Mutex::new(Vec::new()),
        }
    }

    /// Registra un acceso exitoso.
    pub fn registrar_acceso(&self, usuario_id: &str, accion: &str, recurso: &str) {
        let registro = RegistroAuditoria::nuevo(
            usuario_id.to_string(),
            accion.to_string(),
            recurso.to_string(),
            "exitoso".to_string(),
        );
        let mut registros = self.registros.lock().unwrap();
        registros.push(registro);
    }

    /// Registra un intento de acceso denegado.
    pub fn registrar_intento_fallido(&self, usuario_id: &str, accion: &str, recurso: &str) {
        let registro = RegistroAuditoria::nuevo(
            usuario_id.to_string(),
            accion.to_string(),
            recurso.to_string(),
            "denegado".to_string(),
        );
        let mut registros = self.registros.lock().unwrap();
        registros.push(registro);
    }

    /// Obtiene todos los registros auditados.
    pub fn obtener_registros(&self) -> Vec<RegistroAuditoria> {
        let registros = self.registros.lock().unwrap();
        registros.clone()
    }
}


#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_crear_registro_auditoria() {
        let registro = RegistroAuditoria::nuevo(
            "usuario_123".to_string(),
            "ejecutar_herramienta".to_string(),
            "herramienta_sql".to_string(),
            "exitoso".to_string(),
        );
        assert_eq!(registro.usuario_id, "usuario_123");
        assert_eq!(registro.accion, "ejecutar_herramienta");
    }

    #[test]
    fn test_registro_tiene_timestamp() {
        let ahora = SystemTime::now()
            .duration_since(SystemTime::UNIX_EPOCH)
            .unwrap()
            .as_secs();
        
        let registro = RegistroAuditoria::nuevo(
            "user".to_string(),
            "accion".to_string(),
            "recurso".to_string(),
            "exitoso".to_string(),
        );
        
        assert!(registro.timestamp >= ahora);
    }

    #[test]
    fn test_registro_resultado_denegado() {
        let registro = RegistroAuditoria::nuevo(
            "usuario_456".to_string(),
            "cambiar_config".to_string(),
            "config.yaml".to_string(),
            "denegado".to_string(),
        );
        assert_eq!(registro.resultado, "denegado");
    }

    #[test]
    fn test_crear_auditor() {
        let auditor = AuditorRbac::nuevo();
        let registros = auditor.obtener_registros();
        assert_eq!(registros.len(), 0);
    }

    #[test]
    fn test_registrar_acceso() {
        let auditor = AuditorRbac::nuevo();
        auditor.registrar_acceso("usuario_1", "leer_archivo", "datos.txt");

        let registros = auditor.obtener_registros();
        assert_eq!(registros.len(), 1);
        assert_eq!(registros[0].resultado, "exitoso");
    }

    #[test]
    fn test_registrar_intento_fallido() {
        let auditor = AuditorRbac::nuevo();
        auditor.registrar_intento_fallido("usuario_2", "cambiar_config", "config.yaml");

        let registros = auditor.obtener_registros();
        assert_eq!(registros.len(), 1);
        assert_eq!(registros[0].resultado, "denegado");
    }

    #[test]
    fn test_obtener_registros_multiples() {
        let auditor = AuditorRbac::nuevo();
        auditor.registrar_acceso("usuario_1", "accion_1", "recurso_1");
        auditor.registrar_intento_fallido("usuario_2", "accion_2", "recurso_2");
        auditor.registrar_acceso("usuario_3", "accion_3", "recurso_3");

        let registros = auditor.obtener_registros();
        assert_eq!(registros.len(), 3);
        assert_eq!(registros[0].resultado, "exitoso");
        assert_eq!(registros[1].resultado, "denegado");
        assert_eq!(registros[2].resultado, "exitoso");
    }
}
