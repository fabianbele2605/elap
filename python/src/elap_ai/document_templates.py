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
# TEMPLATE REGISTRY
# ============================================================================

DOCUMENT_TEMPLATES = {
    # RRHH
    'manual_empleado': ManualDelEmpleadoTemplate,
    'politica_vacaciones': PoliticaVacacionesTemplate,
    'codigo_conducta': CodigoDeConductaTemplate,
    # Finanzas
    'presupuesto_anual': PresupuestoAnualTemplate,
    'politica_gastos': PoliticaDeGastosTemplate,
    # Operaciones
    'politica_calidad': PoliticaDeCalidadTemplate,
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
