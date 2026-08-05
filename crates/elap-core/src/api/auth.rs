//! Autenticación JWT para API

use jsonwebtoken::{decode, encode, DecodingKey, EncodingKey, Header, Validation};
use serde::{Deserialize, Serialize};
use axum::{
    async_trait,
    extract::FromRequestParts,
    http::{request::Parts, StatusCode},
};
use chrono::{Duration, Utc};

/// Claims del JWT
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Claims {
    /// ID del usuario
    pub sub: String,
    /// Rol del usuario
    pub rol: String,
    /// Tiempo de expiración
    pub exp: i64,
    /// Tiempo de emisión
    pub iat: i64,
}

impl Claims {
    /// Crear nuevos claims
    pub fn nuevo(usuario_id: String, rol: String) -> Self {
        let ahora = Utc::now();
        let expiracion = ahora + Duration::hours(24);

        Self {
            sub: usuario_id,
            rol,
            iat: ahora.timestamp(),
            exp: expiracion.timestamp(),
        }
    }

    /// Verificar si el token ha expirado
    pub fn ha_expirado(&self) -> bool {
        Utc::now().timestamp() > self.exp
    }
}

/// Generador y validador de JWT
pub struct ManagerJWT {
    secret: String,
}

impl ManagerJWT {
    /// Crear nuevo manager con secret
    pub fn nuevo(secret: impl Into<String>) -> Self {
        Self {
            secret: secret.into(),
        }
    }

    /// Generar token JWT
    pub fn generar_token(&self, claims: &Claims) -> Result<String, jsonwebtoken::errors::Error> {
        let key = EncodingKey::from_secret(self.secret.as_ref());
        encode(&Header::default(), claims, &key)
    }

    /// Validar y decodificar token
    pub fn validar_token(&self, token: &str) -> Result<Claims, String> {
        let key = DecodingKey::from_secret(self.secret.as_ref());
        let data = decode::<Claims>(token, &key, &Validation::default())
            .map_err(|e| format!("Token inválido: {}", e))?;

        if data.claims.ha_expirado() {
            return Err("Token expirado".to_string());
        }

        Ok(data.claims)
    }
}

/// Extractor para validar Bearer token
#[async_trait]
impl<S> FromRequestParts<S> for Claims
where
    S: Send + Sync,
{
    type Rejection = (StatusCode, String);

    async fn from_request_parts(parts: &mut Parts, _state: &S) -> Result<Self, Self::Rejection> {
        let header = parts
            .headers
            .get("Authorization")
            .and_then(|h| h.to_str().ok())
            .ok_or((
                StatusCode::UNAUTHORIZED,
                "Missing Authorization header".to_string(),
            ))?;

        let token = header
            .strip_prefix("Bearer ")
            .ok_or((
                StatusCode::UNAUTHORIZED,
                "Invalid Authorization header format".to_string(),
            ))?;

        // Usar secret por defecto para validación
        let manager = ManagerJWT::nuevo("elap-secret-key");
        manager
            .validar_token(token)
            .map_err(|_| (StatusCode::UNAUTHORIZED, "Invalid token".to_string()))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_crear_claims() {
        let claims = Claims::nuevo("user123".to_string(), "Admin".to_string());
        assert_eq!(claims.sub, "user123");
        assert_eq!(claims.rol, "Admin");
        assert!(!claims.ha_expirado());
    }

    #[test]
    fn test_generar_token() {
        let manager = ManagerJWT::nuevo("secret-key");
        let claims = Claims::nuevo("user123".to_string(), "User".to_string());
        let token = manager.generar_token(&claims);
        assert!(token.is_ok());
    }

    #[test]
    fn test_validar_token() {
        let manager = ManagerJWT::nuevo("secret-key");
        let claims = Claims::nuevo("user123".to_string(), "User".to_string());
        let token = manager.generar_token(&claims).unwrap();

        let resultado = manager.validar_token(&token);
        assert!(resultado.is_ok());
        assert_eq!(resultado.unwrap().sub, "user123");
    }

    #[test]
    fn test_token_invalido() {
        let manager = ManagerJWT::nuevo("secret-key");
        let resultado = manager.validar_token("invalid.token.here");
        assert!(resultado.is_err());
        assert!(resultado.unwrap_err().contains("Token inválido"));
    }

    #[test]
    fn test_claims_expiracion() {
        let mut claims = Claims::nuevo("user123".to_string(), "User".to_string());
        claims.exp = (Utc::now() - Duration::hours(1)).timestamp();
        assert!(claims.ha_expirado());
    }
}
