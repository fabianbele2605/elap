# Security Policy

## Reportar vulnerabilidades

**NUNCA** reportes vulnerabilidades públicamente en GitHub Issues.

### Cómo reportar

1. **Email privado:**
   ```
   security@bblabs.io
   ```

2. **Incluye:**
   - Descripción de la vulnerabilidad
   - Versión afectada
   - Pasos para reproducir
   - Impacto potencial
   - Tu información de contacto

3. **Timeline:**
   - Confirmación: 24 horas
   - Fix plan: 5 días
   - Release: 30 días después del fix

### GPG Encryption (Opcional)
Si lo deseas, puedes encriptar con la clave pública de ELAP.

**Contacto alternativo:**
- Twitter DM: @bblabs
- LinkedIn: BBLABS

## Nuestro compromiso

✅ Tomaremos en serio tu reporte  
✅ Investigaremos dentro de 5 días  
✅ Te mantendremos informado  
✅ Haremos fix prioritario  
✅ Publicaremos credit (si quieres)  

## Supported Versions

Reciben parches de seguridad:

| Versión | Status | Soporte hasta |
|---------|--------|---------------|
| 1.5.x   | Actual | 2027-08-06    |
| 1.4.x   | LTS    | 2027-02-06    |
| < 1.4   | End-of-life | No soportado |

## Security Best Practices

### Para usuarios:

✅ **Do:**
- Update regularmente
- Usa HTTPS en producción
- Protege tus API keys
- Revisa logs regularmente
- Usa RBAC role-based access

❌ **Don't:**
- Publiques secrets en código
- Deshabilites autenticación
- Uses versiones old
- Confíes en entrada sin validar
- Expongas puertos sin firewall

### Para desarrolladores:

✅ Valida TODA entrada de usuario  
✅ Usa parametrized queries (SQL injection)  
✅ Encrypta datos sensibles  
✅ Revisa dependencias (cargo audit, pip audit)  
✅ No uses unwrap() en Rust  
✅ Logging sin passwords  
✅ Tests para edge cases  

❌ NO uses eval(), exec()  
❌ NO almacenes contraseñas en plaintext  
❌ NO hagas deploy sin testing  
❌ NO ignores warnings  

## Checklist de seguridad

Antes de cada release:

- [ ] cargo audit (Rust dependencies)
- [ ] pip audit (Python dependencies)
- [ ] Dependencias actualizadas
- [ ] No secrets en código
- [ ] Tests pasan
- [ ] RBAC funciona
- [ ] Logs no exponen data
- [ ] Errors no exponen stack traces

## Divulgación responsable

Si encuentras vulnerabilidad:

1. **NO** la reportes en Issues
2. **SÍ** envía email privado a security@bblabs.io
3. **SÍ** dale tiempo para arreglar (30 días)
4. **SÍ** coordina la publicación

## Gracias

Agradecemos a los investigadores de seguridad que reportan vulnerabilidades de manera responsable.

Tu contribución hace ELAP más seguro para todos.

---

**Última actualización:** 2026-08-06  
**Contacto:** security@bblabs.io
