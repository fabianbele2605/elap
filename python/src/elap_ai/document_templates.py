"""
Plantillas de documentos para generación automática basada en configuración de empresa.

Cada template recibe CompanyConfig y genera un documento personalizado.
"""

from typing import Dict, Any
from datetime import datetime


class DocumentTemplate:
    """Base class para templates de documentos."""

    @staticmethod
    def render(config: Dict[str, Any]) -> str:
        """Render template with company config."""
        raise NotImplementedError


# ============================================================================
# RRHH TEMPLATES (5)
# ============================================================================


class ManualDelEmpleadoTemplate(DocumentTemplate):
    @staticmethod
    def render(config: Dict[str, Any]) -> str:
        return f"""
# MANUAL DEL EMPLEADO

## {config['nombreEmpresa']}

### 1. BIENVENIDA

Bienvenido a {config['nombreEmpresa']}. Nos complace contar con tu incorporación a nuestro equipo.

Desde nuestra fundación en {config['anoFundacion']}, hemos sido líderes en el sector de {config['sector']}
con presencia en {config['ubicacion']}. Con {config['numEmpleados']} empleados,
continuamos creciendo y fortaleciendo nuestro equipo de trabajo.

### 2. NUESTRA MISIÓN Y VALORES

**Misión:** Proveer soluciones innovadoras en {config['sector']} que agreguen valor a nuestros clientes.

**Valores:**
- Integridad: Actuamos con honestidad en todas nuestras acciones
- Excelencia: Buscamos calidad en cada aspecto de nuestro trabajo
- Colaboración: Trabajamos juntos hacia objetivos comunes
- Innovación: Promovemos ideas creativas y mejora continua

### 3. ESTRUCTURA ORGANIZACIONAL

Nuestros departamentos principales son:

{', '.join(config.get('departamentos', []))}

### 4. BENEFICIOS Y COMPENSACIÓN

- **Salario Base:** ${config['salarioPromedio']:,} COP mensuales
- **Vacaciones:** 15 días al año
- **Seguro de Salud:** Cobertura integral para ti y tu familia
- **Bonificación:** Anual según desempeño
- **Flexibilidad Laboral:** Permitimos trabajo remoto según políticas

### 5. DERECHOS Y DEBERES

**Derechos:**
- Derecho a un ambiente laboral seguro
- Derecho a capacitación profesional
- Derecho a no discriminación
- Derecho a privacidad y confidencialidad

**Deberes:**
- Cumplir con horarios establecidos
- Mantener confidencialidad de información
- Respetar a colegas y superiores
- Contribuir al ambiente laboral positivo

### 6. POLÍTICAS DE COMPORTAMIENTO

Se espera que todos los empleados mantengan un comportamiento profesional en todo momento.

Generado automáticamente por ELAP — {datetime.now().strftime('%d/%m/%Y')}
"""


class PoliticaVacacionesTemplate(DocumentTemplate):
    @staticmethod
    def render(config: Dict[str, Any]) -> str:
        return f"""
# POLÍTICA DE VACACIONES

## {config['nombreEmpresa']}

### 1. OBJETIVO

Establecer los lineamientos para el disfrute de vacaciones de los empleados, permitiendo
descanso y recuperación para mantener productividad.

### 2. DERECHOS A VACACIONES

Todo empleado con contrato laboral permanente tiene derecho a:

- **15 días calendario** de vacaciones remuneradas al año
- **Acumulación:** Los días no disfrutados en el año se acumulan hasta por 2 años
- **Pago:** Durante vacaciones se paga el salario completo
- **Bonificación especial:** 10% adicional si se disfruta en el período programado

### 3. CÁLCULO DE DÍAS

Los días de vacaciones se calculan como:

```
Días = (Días trabajados en el año × 15) / 365
```

**Ejemplo:** Si trabajaste 200 días, tienes derecho a:
(200 × 15) / 365 = 8.2 días ≈ 8 días

### 4. PROCEDIMIENTO DE SOLICITUD

1. Solicitar con **30 días de anticipación** mínimo
2. Completar formulario de solicitud de vacaciones
3. Obtener aprobación del gerente inmediato
4. Coordinar cobertura del puesto
5. Confirmar con RRHH

### 5. RESTRICCIONES

- No se pueden tomar más de 5 días consecutivos sin aprobación del CEO
- No se acumulan más de 30 días
- No se pueden vender días no disfrutados

### 6. CASOS ESPECIALES

**Casos donde NO se reconocen vacaciones:**
- Despido disciplinario
- Abandono de cargo
- Incapacidad mayor a 6 meses

**Casos donde SÍ se reconocen vacaciones:**
- Terminación por causa empresarial
- Renuncia voluntaria
- Jubilación

Generado automáticamente por ELAP — {datetime.now().strftime('%d/%m/%Y')}
"""


class CodigoDeConductaTemplate(DocumentTemplate):
    @staticmethod
    def render(config: Dict[str, Any]) -> str:
        return f"""
# CÓDIGO DE CONDUCTA

## {config['nombreEmpresa']}

### 1. INTRODUCCIÓN

Este código establece las expectativas de comportamiento ético y profesional
para todos los empleados de {config['nombreEmpresa']}.

### 2. PRINCIPIOS FUNDAMENTALES

**Integridad:** Actuar con honestidad y transparencia en todas las circunstancias.

**Respeto:** Valorar la dignidad y derechos de todos, sin discriminación.

**Profesionalismo:** Mantener altos estándares de calidad y responsabilidad.

**Confidencialidad:** Proteger información confidencial de la empresa y clientes.

### 3. CONDUCTA ESPERADA

Los empleados deben:

- Tratar con respeto a colegas, supervisores y clientes
- No tolerar acoso, discriminación o intimidación
- Reportar violaciones de este código
- Mantener ambiente laboral profesional
- Cumplir leyes y regulaciones aplicables
- Usar equipos de empresa únicamente para propósitos autorizados

### 4. CONDUCTA PROHIBIDA

Se prohíbe explícitamente:

- Acoso o discriminación por cualquier motivo
- Violencia o amenazas
- Consumo de alcohol o drogas en el trabajo
- Fraude o deshonestidad
- Divulgación de información confidencial
- Represalias contra denunciantes

### 5. SANCIONES

**Violaciones leves:**
- Advertencia verbal
- Advertencia por escrito
- Suspensión temporal

**Violaciones graves:**
- Suspensión extendida
- Terminación inmediata
- Acciones legales según corresponda

### 6. REPORTAR VIOLACIONES

Para reportar violaciones del código, contacta a:

**Departamento RRHH:** {config.get('contactoRRHH', '[RRHH Contact]')}

Todo reporte será manejado con confidencialidad.

Generado automáticamente por ELAP — {datetime.now().strftime('%d/%m/%Y')}
"""


# ============================================================================
# FINANZAS TEMPLATES (3)
# ============================================================================


class PresupuestoAnualTemplate(DocumentTemplate):
    @staticmethod
    def render(config: Dict[str, Any]) -> str:
        presupuesto = config.get('presupuestoAnual', 500000000)
        ano = datetime.now().year + 1

        return f"""
# PRESUPUESTO ANUAL {ano}

## {config['nombreEmpresa']}

### PRESUPUESTO GENERAL

**Presupuesto Total:** ${presupuesto:,} COP

Distribución por departamento:

| Departamento | Asignación | % del Total |
|---|---|---|
| RRHH | ${presupuesto * 0.15:,.0f} | 15% |
| Operaciones | ${presupuesto * 0.35:,.0f} | 35% |
| Ventas & Marketing | ${presupuesto * 0.30:,.0f} | 30% |
| Tecnología | ${presupuesto * 0.15:,.0f} | 15% |
| Administración | ${presupuesto * 0.05:,.0f} | 5% |

### GASTOS OPERACIONALES

**Nómina:** ${presupuesto * 0.50:,.0f} (50%)
- Salarios base
- Beneficios
- Capacitación

**Operaciones:** ${presupuesto * 0.25:,.0f} (25%)
- Renta y servicios
- Mantenimiento
- Suministros

**Ventas:** ${presupuesto * 0.15:,.0f} (15%)
- Marketing
- Publicidad
- Viajes

**Administración:** ${presupuesto * 0.10:,.0f} (10%)
- Servicios profesionales
- Seguros
- Misceláneos

### PROYECCIONES

Con crecimiento esperado de {config.get('crecimientoEsperado', '15-20%')},
esperamos aumentar ingresos en {config.get('crecimientoEsperado', '15-20%')} durante {ano}.

Generado automáticamente por ELAP — {datetime.now().strftime('%d/%m/%Y')}
"""


class PoliticaDeGastosTemplate(DocumentTemplate):
    @staticmethod
    def render(config: Dict[str, Any]) -> str:
        return f"""
# POLÍTICA DE GASTOS

## {config['nombreEmpresa']}

### 1. OBJETIVO

Establecer lineamientos para control y autorización de gastos operacionales.

### 2. LÍMITES DE GASTOS

Por categoría mensual:

| Categoría | Límite Sin Aprobación | Con Aprobación |
|---|---|---|
| Viajes | $2,000,000 | Ilimitado |
| Eventos | $5,000,000 | Ilimitado |
| Tecnología | $1,000,000 | Ilimitado |
| Suministros | $500,000 | Ilimitado |
| Otros | $200,000 | $5,000,000 |

### 3. PROCEDIMIENTO DE APROBACIÓN

1. Gasto < $500,000: Aprobación del supervisor
2. Gasto $500,000 - $2,000,000: Aprobación del gerente
3. Gasto > $2,000,000: Aprobación del CFO

### 4. DOCUMENTACIÓN

Todos los gastos requieren:

- Factura o recibo original
- Descripción del gasto
- Justificación comercial
- Aprobaciones requeridas

### 5. REEMBOLSO

- Plazo de presentación: Máximo 30 días
- Plazo de pago: 15 días después de aprobación
- Documentación incompleta: Negación de reembolso

Generado automáticamente por ELAP — {datetime.now().strftime('%d/%m/%Y')}
"""


# ============================================================================
# OPERACIONES TEMPLATES (4)
# ============================================================================


class PoliticaDeCalidadTemplate(DocumentTemplate):
    @staticmethod
    def render(config: Dict[str, Any]) -> str:
        return f"""
# POLÍTICA DE CALIDAD

## {config['nombreEmpresa']}

### 1. COMPROMISOS DE CALIDAD

Nos comprometemos a:

- Satisfacer necesidades de clientes
- Cumplir regulaciones aplicables
- Mejorar continuamente procesos
- Desarrollar competencias del personal

### 2. ESTÁNDARES MÍNIMOS

Todos los productos/servicios deben cumplir:

- **Entrega a tiempo:** 100% de órdenes on-time
- **Defectos:** < 0.1% de defectos
- **Satisfacción:** NPS > 70

### 3. AUDITORÍAS

Se realizan auditorías internas:

- **Trimestrales:** Verificación de procesos
- **Anuales:** Auditoría completa del sistema
- **Según necesidad:** Auditorías específicas

### 4. ACCIONES CORRECTIVAS

Cuando se detectan no-conformidades:

1. Registro de problema
2. Investigación de causa raíz
3. Plan de acción correctiva
4. Implementación
5. Verificación de efectividad
6. Cierre del caso

Generado automáticamente por ELAP — {datetime.now().strftime('%d/%m/%Y')}
"""


# ============================================================================
# RRHH TEMPLATES (5) — 2 MÁS
# ============================================================================


class PoliticaDeAusenciasTemplate(DocumentTemplate):
    @staticmethod
    def render(config: Dict[str, Any]) -> str:
        return f"""
# POLÍTICA DE AUSENCIAS

## {config['nombreEmpresa']}

### 1. OBJETIVO

Establecer procedimientos para manejo de ausencias del personal, incluyendo
incapacidades, permisos y licencias.

### 2. TIPOS DE AUSENCIA

**Incapacidades:**
- Enfermedad: Requerida incapacidad médica
- Máximo 3 días consecutivos sin aprobación
- Después de 3 días: Requiere certificado médico

**Permisos:**
- Personal: Hasta 2 horas/mes sin afectar salario
- Familiares: Hasta 1 día por evento (matrimonio, defunción)
- Médicos: Consultas programadas (máximo 1 por mes)

**Licencias:**
- Maternidad: 12 semanas remuneradas
- Paternidad: 8 días remunerados
- Calamidad doméstica: Hasta 5 días según severidad

### 3. PROCEDIMIENTO DE NOTIFICACIÓN

1. Notificar al supervisor inmediatamente
2. Enviar justificante a RRHH dentro de 24h
3. Para incapacidades > 3 días: Certificado médico obligatorio
4. Confirmación de RRHH al empleado

### 4. DESCUENTOS

- Ausentismo no justificado: Descuento de 1 día de salario
- Después de 3 ausencias injustificadas: Amonestación escrita
- Después de 5: Suspensión o despido disciplinario

### 5. EXCEPCIONES

- Emergencias médicas: No aplica descuento si se justifica en 24h
- Actos legales: Considerados ausentismo justificado

Generado automáticamente por ELAP — {datetime.now().strftime('%d/%m/%Y')}
"""


class ProcedimientoDeContratacionTemplate(DocumentTemplate):
    @staticmethod
    def render(config: Dict[str, Any]) -> str:
        return f"""
# PROCEDIMIENTO DE CONTRATACIÓN

## {config['nombreEmpresa']}

### 1. PROPÓSITO

Estandarizar el proceso de selección, evaluación e incorporación de nuevo personal.

### 2. REQUISITOS PREVIOS

Antes de abrir convocatoria:

- Aprobación presupuestal del puesto
- Descripción clara de funciones
- Definición de competencias requeridas
- Salario autorizado

### 3. ETAPAS DE SELECCIÓN

**Etapa 1: Reclutamiento (1-2 semanas)**
- Publicación en bolsas de empleo
- Invitación de candidatos internos
- Cierre de convocatoria
- Preselección inicial

**Etapa 2: Evaluación Técnica (1 semana)**
- Revisión de hojas de vida
- Pruebas técnicas/de competencias
- Entrevistas técnicas
- Selección de finalistas

**Etapa 3: Entrevista Final (3-5 días)**
- Entrevista con gerente
- Entrevista con CEO/Junta
- Verificación de referencias
- Oferta condicional

**Etapa 4: Incorporación (1 semana)**
- Firma de contrato
- Prueba psicotécnica
- Examen médico
- Inducción

### 4. CRITERIOS DE SELECCIÓN

- Experiencia relevante: Mínimo requerido
- Competencias técnicas: Evaluación práctica
- Competencias blandas: Entrevista comportamental
- Compatibilidad cultural: Allineación con valores

### 5. TIEMPOS MÁXIMOS

- Reclutamiento a oferta: 21 días
- Oferta a incorporación: 14 días
- Total proceso: 35 días máximo

Generado automáticamente por ELAP — {datetime.now().strftime('%d/%m/%Y')}
"""


# ============================================================================
# FINANZAS TEMPLATES (3) — 1 MÁS
# ============================================================================


class ReportesFinancierosTemplate(DocumentTemplate):
    @staticmethod
    def render(config: Dict[str, Any]) -> str:
        ano = datetime.now().year
        ingresos = config.get('presupuestoAnual', 500000000) * 1.1
        gastos = config.get('presupuestoAnual', 500000000)
        utilidad = ingresos - gastos

        return f"""
# REPORTES FINANCIEROS {ano}

## {config['nombreEmpresa']}

### ESTADO DE RESULTADOS

| Concepto | Valor |
|----------|-------|
| **Ingresos por ventas** | ${ingresos:,.0f} |
| Menos: Costo de ventas | ${ingresos * 0.45:,.0f} |
| **Utilidad bruta** | ${ingresos * 0.55:,.0f} |
| Menos: Gastos operacionales | ${gastos * 0.40:,.0f} |
| **Utilidad operacional** | ${ingresos * 0.15:,.0f} |
| Menos: Impuestos (30%) | ${(ingresos * 0.15) * 0.30:,.0f} |
| **Utilidad neta** | ${utilidad * 0.70:,.0f} |

### ANÁLISIS DE RENDIMIENTO

**Margen de Utilidad Neta:** {(utilidad / ingresos * 100):.1f}%
- Target: 15-20%
- Performance: {"NORMAL" if 10 < (utilidad / ingresos * 100) < 25 else "REQUIERE ATENCIÓN"}

**Crecimiento Esperado:** {config.get('crecimientoEsperado', '15-20%')}
- Estrategia: Expansión de mercados
- Inversión requerida: ${ingresos * 0.20:,.0f}

### FLUJO DE CAJA PROYECTADO

**Trimestre Q1:** ${ingresos * 0.25:,.0f}
**Trimestre Q2:** ${ingresos * 0.30:,.0f}
**Trimestre Q3:** ${ingresos * 0.22:,.0f}
**Trimestre Q4:** ${ingresos * 0.23:,.0f}

### RATIOS FINANCIEROS

- Rentabilidad sobre activos (ROA): 12.5%
- Rentabilidad sobre patrimonio (ROE): 18.3%
- Razón de liquidez: 1.8x
- Razón de endeudamiento: 0.6x

Generado automáticamente por ELAP — {datetime.now().strftime('%d/%m/%Y')}
"""


# ============================================================================
# OPERACIONES TEMPLATES (4) — 3 MÁS
# ============================================================================


class MatrizDeProcesosTemplate(DocumentTemplate):
    @staticmethod
    def render(config: Dict[str, Any]) -> str:
        return f"""
# MATRIZ DE PROCESOS

## {config['nombreEmpresa']}

### PROCESOS ESTRATÉGICOS

| Proceso | Responsable | Frecuencia | KPI |
|---------|-------------|-----------|-----|
| Planeación Estratégica | CEO | Anual | Cumplimiento de metas |
| Gestión de Portafolio | CTO | Trimestral | Rentabilidad por producto |
| Análisis de Mercado | Marketing | Mensual | Participación de mercado |

### PROCESOS CLAVE

| Proceso | Responsable | Frecuencia | KPI |
|---------|-------------|-----------|-----|
| Gestión de Ventas | Ventas | Diaria | Cumplimiento de cuota |
| Servicio al Cliente | Operaciones | 24/7 | NPS > 70 |
| Desarrollo de Productos | Ingeniería | Contínuo | Entrega a tiempo |
| Gestión de Inventario | Logística | Diaria | Rotación óptima |
| Gestión de Calidad | Operaciones | Diaria | Defectos < 0.1% |

### PROCESOS DE APOYO

| Proceso | Responsable | Frecuencia | KPI |
|---------|-------------|-----------|-----|
| Gestión de RRHH | RRHH | Mensual | Rotación <10% |
| Gestión Financiera | Contabilidad | Semanal | Reporte a tiempo |
| Gestión de TI | IT | Contínuo | Uptime > 99.5% |
| Auditoría Interna | Auditoría | Trimestral | Hallazgos resueltos |

### INTERACCIONES DE PROCESOS

```
Estratégicos (Dirección General)
    ↓
Clave (Generadores de valor)
    ↓
Apoyo (Sustentadores)
```

Generado automáticamente por ELAP — {datetime.now().strftime('%d/%m/%Y')}
"""


class ProcedimientosOperacionalesTemplate(DocumentTemplate):
    @staticmethod
    def render(config: Dict[str, Any]) -> str:
        return f"""
# PROCEDIMIENTOS OPERACIONALES

## {config['nombreEmpresa']}

### 1. GESTIÓN DE PEDIDOS

**Paso 1:** Recepción de solicitud
- Validar formato de pedido
- Verificar cliente en base de datos
- Asignar número de referencia

**Paso 2:** Confirmación de disponibilidad
- Consultar inventario
- Validar capacidad de producción
- Confirmar fecha de entrega

**Paso 3:** Procesamiento
- Crear orden de compra
- Enviar a almacén/producción
- Notificar al cliente

**Paso 4:** Entrega
- Empacar según estándares
- Generar documentos
- Seguimiento hasta destino

**SLA:** 95% de pedidos entregados a tiempo

### 2. GESTIÓN DE DEVOLUCIONES

**Causas aceptadas:**
- Producto defectuoso
- Entrega incorrecta
- Cambio de cliente (hasta 5 días)

**Procedimiento:**
1. Cliente reporta en línea/teléfono
2. RRHH genera RMA
3. Inspección de producto
4. Reembolso/reemplazo en 10 días

### 3. CONTROL DE CALIDAD

**Inspección en Entrada:**
- 100% de materias primas
- Revisión contra especificaciones
- Rechazo si no cumple

**Inspección en Proceso:**
- Muestreo cada 2 horas
- Verificación de parámetros críticos
- Documentación obligatoria

**Inspección Final:**
- Revisión de empaque
- Prueba funcional (si aplica)
- Etiquetado correcto

Generado automáticamente por ELAP — {datetime.now().strftime('%d/%m/%Y')}
"""


class PoliticaDeComprasTemplate(DocumentTemplate):
    @staticmethod
    def render(config: Dict[str, Any]) -> str:
        return f"""
# POLÍTICA DE COMPRAS

## {config['nombreEmpresa']}

### 1. OBJETIVO

Asegurar que todas las compras se realicen de forma ética, eficiente y económica
manteniendo estándares de calidad.

### 2. AUTORIZACIÓN POR MONTO

| Monto | Autorización | Proceso |
|------|---|---|
| < $500,000 | Jefe de área | 1 cotización |
| $500K - $2M | Gerente | 2 cotizaciones |
| $2M - $10M | Director | 3 cotizaciones competitivas |
| > $10M | CEO + Junta | Licitación abierta |

### 3. PROCESO DE COMPRA

1. **Solicitud**
   - Requisición con especificaciones
   - Aprobación del presupuesto
   - Justificación comercial

2. **Cotización**
   - Obtener ofertas de 2-3 proveedores
   - Comparar precio, calidad, plazo
   - Documentar análisis

3. **Orden**
   - Generar PO con términos claros
   - Enviar a proveedor seleccionado
   - Confirmar recepción

4. **Recepción**
   - Inspección de calidad
   - Verificar cantidad
   - Revisar factura

5. **Pago**
   - Procesar contra factura
   - Cumplir términos de crédito
   - Documentar gasto

### 4. SELECCIÓN DE PROVEEDORES

Criterios de evaluación:
- Precio competitivo (40%)
- Calidad certificada (30%)
- Entrega a tiempo (20%)
- Servicio post-venta (10%)

### 5. TÉRMINOS Y CONDICIONES

- **Plazo de pago:** 30 días neto
- **Descuentos por volumen:** Negociables
- **Retenciones:** 8% impuesto a la renta
- **Garantía:** Mínimo 1 año en equipos

Generado automáticamente por ELAP — {datetime.now().strftime('%d/%m/%Y')}
"""


# ============================================================================
# LEGAL TEMPLATES (2)
# ============================================================================


class TerminosYCondicionesTemplate(DocumentTemplate):
    @staticmethod
    def render(config: Dict[str, Any]) -> str:
        return f"""
# TÉRMINOS Y CONDICIONES

## {config['nombreEmpresa']}

**Última actualización:** {datetime.now().strftime('%d de %B de %Y')}

### 1. ACEPTACIÓN

Al acceder y utilizar este sitio web o servicios de {config['nombreEmpresa']},
aceptas estar legalmente vinculado por estos términos y condiciones.

### 2. USO PERMITIDO

El usuario se compromete a:
- Usar los servicios solo para fines legítimos
- No reproducir ni distribuir contenido sin autorización
- No intentar acceso no autorizado a sistemas
- Cumplir todas las leyes aplicables

### 3. LIMITACIÓN DE RESPONSABILIDAD

{config['nombreEmpresa']} no será responsable por:
- Daños indirectos, incidentales o consecuentes
- Pérdida de datos o ingresos
- Interrupciones del servicio por causas externas

### 4. PROPIEDAD INTELECTUAL

Todo contenido (textos, imágenes, software) es propiedad de {config['nombreEmpresa']}
y está protegido por derechos de autor. No está permitida la reproducción
sin permiso escrito.

### 5. PRIVACIDAD

Consultar Política de Privacidad para información sobre:
- Recopilación de datos
- Uso de información
- Derechos del usuario

### 6. MODIFICACIONES

{config['nombreEmpresa']} se reserva el derecho de modificar estos términos.
Los cambios serán notificados con 15 días de anticipación.

### 7. RESOLUCIÓN DE DISPUTAS

- Primer intento: Resolución amigable
- Si falla: Mediación
- Última instancia: Arbitraje conforme a leyes locales

Generado automáticamente por ELAP — {datetime.now().strftime('%d/%m/%Y')}
"""


class PoliticaDePrivacidadTemplate(DocumentTemplate):
    @staticmethod
    def render(config: Dict[str, Any]) -> str:
        return f"""
# POLÍTICA DE PRIVACIDAD

## {config['nombreEmpresa']}

**Efectiva desde:** {datetime.now().strftime('%d de %B de %Y')}

### 1. INFORMACIÓN QUE RECOPILAMOS

Podemos recopilar:
- Información de identificación personal (nombre, email, teléfono)
- Información de transacciones (compras, pagos)
- Información técnica (IP, cookies, navegador)
- Información de preferencias (mediante formularios)

### 2. USO DE INFORMACIÓN

Utilizamos información para:
- Prestar servicios solicitados
- Mejorar nuestros productos/servicios
- Comunicaciones de marketing (con consentimiento)
- Análisis estadísticos
- Cumplimiento legal

### 3. PROTECCIÓN DE DATOS

Implementamos medidas:
- Encriptación SSL en transferencias
- Control de acceso basado en roles
- Auditorías de seguridad regulares
- Capacitación en privacidad del personal

### 4. DERECHOS DEL USUARIO

Tienes derecho a:
- Acceder a tus datos personales
- Solicitar corrección de inexactitudes
- Pedir eliminación (derecho al olvido)
- Portabilidad de datos
- Retirar consentimiento en cualquier momento

### 5. COOKIES

Usamos cookies para:
- Preferencias del usuario
- Sesiones de usuario
- Análisis de tráfico
- Publicidad personalizada

Los usuarios pueden desactivar cookies en su navegador.

### 6. RETENCIÓN DE DATOS

- Datos de transacciones: 7 años (requisito fiscal)
- Datos de contacto: Mientras active la cuenta
- Cookies: Según configuración del navegador

### 7. TERCEROS

No compartimos información con terceros excepto:
- Proveedores de servicios (bajo contrato)
- Cuando la ley lo requiere
- Con consentimiento explícito del usuario

### 8. CAMBIOS A ESTA POLÍTICA

Notificaremos cambios importantes 30 días antes de implementar.

**Contacto Privacidad:** {config.get('contactoRRHH', '[contact]')}

Generado automáticamente por ELAP — {datetime.now().strftime('%d/%m/%Y')}
"""


# ============================================================================
# VENTAS TEMPLATES (1)
# ============================================================================


class EstrategiaComercialTemplate(DocumentTemplate):
    @staticmethod
    def render(config: Dict[str, Any]) -> str:
        return f"""
# ESTRATEGIA COMERCIAL

## {config['nombreEmpresa']}

**Año Fiscal:** {datetime.now().year}

### 1. VISIÓN Y OBJETIVOS

**Visión:** Ser líderes en {config['sector']} reconocidos por innovación y servicio.

**Objetivos Comerciales {datetime.now().year}:**
- Incrementar ingresos {config.get('crecimientoEsperado', '15-20%')}
- Expandir a 2 nuevos mercados geográficos
- Aumentar participación de mercado en 5%
- Mejorar retención de clientes a 95%

### 2. SEGMENTACIÓN DE CLIENTES

**Segmento Premium:**
- Grandes empresas, ingresos > $100M
- Margen: 35%
- Target: 20% de cartera

**Segmento Enterprise:**
- Empresas medianas, ingresos $10-100M
- Margen: 28%
- Target: 50% de cartera

**Segmento SME:**
- Pequeñas empresas, ingresos < $10M
- Margen: 20%
- Target: 30% de cartera

### 3. PRODUCTOS Y SERVICIOS

**Productos Principales:**
{', '.join(config.get('productos', ['Producto A', 'Producto B']))}

**Servicios Complementarios:**
{', '.join(config.get('servicios', ['Servicio A', 'Servicio B']))}

**Clientes Clave:**
{config.get('clientesPrincipales', 'A definir')}

### 4. ESTRATEGIA DE PRECIOS

- Penetración en nuevos mercados: -10% introductorio
- Productos existentes: Aumento inflacionario + 2%
- Servicios premium: +15% vs competencia

### 5. CANALES DE DISTRIBUCIÓN

- Venta directa: 40%
- Distribuidores: 35%
- Online: 25%

### 6. PLAN DE MARKETING

**Campañas {datetime.now().year}:**
- Q1: Lanzamiento de nuevos productos
- Q2: Expansión geográfica
- Q3: Retención y upsell
- Q4: Consolidación de logros

**Budget Estimado:** ${config.get('presupuestoAnual', 500000000) * 0.15:,.0f}

### 7. MÉTRICAS DE ÉXITO

- Revenue crecimiento: {config.get('crecimientoEsperado', '15-20%')}
- Customer Acquisition Cost (CAC): < ${config.get('salarioPromedio', 3000000) * 5:,.0f}
- Lifetime Value (LTV): > ${config.get('salarioPromedio', 3000000) * 20:,.0f}
- Net Promoter Score (NPS): > 70
- Churn rate: < 5% anual

Generado automáticamente por ELAP — {datetime.now().strftime('%d/%m/%Y')}
"""


# ============================================================================
# TEMPLATE REGISTRY
# ============================================================================

DOCUMENT_TEMPLATES = {
    # RRHH (5)
    'manual_empleado': ManualDelEmpleadoTemplate,
    'politica_vacaciones': PoliticaVacacionesTemplate,
    'codigo_conducta': CodigoDeConductaTemplate,
    'politica_ausencias': PoliticaDeAusenciasTemplate,
    'procedimiento_contratacion': ProcedimientoDeContratacionTemplate,
    # Finanzas (3)
    'presupuesto_anual': PresupuestoAnualTemplate,
    'politica_gastos': PoliticaDeGastosTemplate,
    'reportes_financieros': ReportesFinancierosTemplate,
    # Operaciones (4)
    'politica_calidad': PoliticaDeCalidadTemplate,
    'matriz_procesos': MatrizDeProcesosTemplate,
    'procedimientos_operacionales': ProcedimientosOperacionalesTemplate,
    'politica_compras': PoliticaDeComprasTemplate,
    # Legal (2)
    'terminos_condiciones': TerminosYCondicionesTemplate,
    'politica_privacidad': PoliticaDePrivacidadTemplate,
    # Ventas (1)
    'estrategia_comercial': EstrategiaComercialTemplate,
}


def generar_documento(template_name: str, config: Dict[str, Any]) -> str:
    """Genera un documento usando el template especificado."""
    if template_name not in DOCUMENT_TEMPLATES:
        raise ValueError(f"Template no encontrado: {template_name}")

    template_class = DOCUMENT_TEMPLATES[template_name]
    return template_class.render(config)


def generar_todos_documentos(config: Dict[str, Any]) -> Dict[str, str]:
    """Genera todos los documentos para una configuración de empresa."""
    documentos = {}

    for template_name in DOCUMENT_TEMPLATES.keys():
        try:
            documentos[template_name] = generar_documento(template_name, config)
        except Exception as e:
            print(f"Error generando {template_name}: {e}")
            documentos[template_name] = ""

    return documentos
