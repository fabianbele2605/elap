/**
 * Contexto Empresarial para Agentes ELAP
 * Empresa: Distribuidora Andina Foods S.A.S.
 * Ubicación: Barranquilla, Colombia
 * Generado: 2026-08-07
 */

export const EMPRESA_CONTEXTO = {
  nombre: "Distribuidora Andina Foods S.A.S.",
  nombreComercial: "Andina Foods",
  nit: "900.487.213-5",
  tipoSociedad: "Sociedad por Acciones Simplificada (S.A.S.)",
  fundacion: 2011,
  representanteLegal: "Carlos Andrés Meléndez Ruiz",

  descripcion: `Empresa colombiana dedicada a la comercialización, distribución y venta de productos
de consumo masivo (alimentos, bebidas, aseo del hogar y cuidado personal) para el canal tradicional,
retail organizado e institucional en la región Caribe.`,

  sector: "Comercio al por mayor de productos de consumo masivo (FMCG)",
  clasificacion: "Mediana empresa",
  empleados: 187,
  cobertura: ["Atlántico", "Bolívar", "Magdalena", "La Guajira"],
  clientesActivos: 1450,

  ubicaciones: {
    sede: "Calle 76 # 54-32, Edificio Torre Caribe, Piso 6, Barranquilla",
    cedi: "Parque Industrial Las Flores, Bodega 12, Vía 40, Barranquilla",
    cartagena: "Zona Industrial Mamonal, Km 3, Cartagena",
    santaMarta: "Carrera 21 # 22-18, Santa Marta"
  },

  horarios: {
    lunes_viernes: "7:00 a.m. – 5:30 p.m.",
    sabados: "7:00 a.m. – 12:00 p.m."
  },

  mision: `Conectar a los productores de consumo masivo con el comercio de la región Caribe,
garantizando disponibilidad, cobertura y servicio de excelencia, generando valor sostenible
para clientes, colaboradores y accionistas.`,

  vision: `Ser en 2030 el distribuidor de consumo masivo líder en la región Caribe colombiana,
reconocido por su eficiencia logística, innovación comercial y cercanía con el tendero.`,

  valores: [
    "Integridad: actuar con transparencia y ética en cada relación comercial",
    "Orientación al cliente: entender y anticipar las necesidades del canal",
    "Excelencia operativa: cumplir con precisión los compromisos de entrega",
    "Trabajo en equipo: colaboración entre áreas para lograr resultados",
    "Innovación: adoptar tecnología y mejores prácticas de forma continua",
    "Sostenibilidad: gestión responsable de recursos e impacto ambiental"
  ],

  estructura: {
    presidente: "Ricardo Alfonso Meléndez Cabrera",
    miembrosJunta: 3,
    gerencias: [
      {
        cargo: "Gerente General (CEO)",
        nombre: "Carlos Andrés Meléndez Ruiz",
        reporta: "Junta Directiva",
        aCargoPersonas: 0
      },
      {
        cargo: "Gerente Financiero y Administrativo",
        nombre: "Diana Patricia Osorio Cantillo",
        reporta: "Gerente General",
        aCargoPersonas: 12
      },
      {
        cargo: "Gerente Comercial y de Ventas",
        nombre: "Jorge Luis Herrera Barros",
        reporta: "Gerente General",
        aCargoPersonas: 68
      },
      {
        cargo: "Gerente de Operaciones y Logística",
        nombre: "Marcela Isabel Torres Pacheco",
        reporta: "Gerente General",
        aCargoPersonas: 79
      },
      {
        cargo: "Gerente de Talento Humano",
        nombre: "Andrés Felipe Cárdenas Molina",
        reporta: "Gerente General",
        aCargoPersonas: 9
      },
      {
        cargo: "Jefe de Tecnología (TI)",
        nombre: "Laura Sofía Restrepo Vega",
        reporta: "Gerente General",
        aCargoPersonas: 6
      }
    ]
  },

  productos: {
    marcasTerceros: [
      "Alimentos empacados: pastas, enlatados, snacks, galletería",
      "Lácteos y refrigerados: quesos, yogures, embutidos",
      "Bebidas: gaseosas, jugos, agua embotellada, cervezas",
      "Aseo del hogar y cuidado personal: detergentes, jabones"
    ],
    marcaPropia: "Andina Selecta (arroz, pastas, enlatados)",
    servicios: [
      "Distribución y logística de última milla",
      "Trade marketing y mercadeo en punto de venta",
      "Crédito comercial a tenderos",
      "Inteligencia de mercado y reportes de rotación"
    ]
  },

  financieros: {
    ingresos2024: "$18.500 MM",
    ingresos2025: "$21.200 MM",
    utilidad2024: "$980 MM",
    utilidad2025: "$1.260 MM",
    margenNeto: "5,9%",
    empleados: 187
  },

  procesosRRHH: {
    reclutamiento: [
      "Requisición de personal",
      "Reclutamiento y filtro CV",
      "Entrevistas y pruebas psicotécnicas",
      "Verificación de referencias",
      "Contratación y afiliación"
    ],
    desarrollo: [
      "Inducción corporativa",
      "Entrenamiento en puesto",
      "Evaluaciones semestrales",
      "Plan de capacitación continua",
      "Desvinculación y liquidación"
    ],
    beneficios: [
      "Seguridad social obligatoria",
      "Plan complementario de pensión",
      "Caja de compensación",
      "Fondo de solidaridad",
      "Capacitación y desarrollo",
      "Clima laboral y bienestar"
    ]
  },

  politicas: [
    "Crédito y cartera: cupos 30-45 días",
    "Calidad: control de vencimiento y trazabilidad",
    "SST: cumplimiento Decreto 1072/2015",
    "Protección de datos: Ley 1581/2012",
    "Anticorrupción y ética empresarial",
    "Código de buen gobierno corporativo",
    "Teletrabajo: 2 días remotos/semana (admin)",
    "Ambiental: reciclaje y eficiencia energética",
    "Seguridad de la información"
  ]
};

/**
 * Contexto para System Prompt de agentes
 * Se inyecta automáticamente en cada pregunta
 */
export const SISTEMA_PROMPT_EMPRESA = `
CONTEXTO EMPRESARIAL:

Empresa: ${EMPRESA_CONTEXTO.nombre}
Sector: ${EMPRESA_CONTEXTO.sector}
Ubicación: ${EMPRESA_CONTEXTO.ubicaciones.sede}
Empleados: ${EMPRESA_CONTEXTO.empleados}
Clientes activos: ${EMPRESA_CONTEXTO.clientesActivos}

MISIÓN:
${EMPRESA_CONTEXTO.mision}

VALORES CORPORATIVOS:
${EMPRESA_CONTEXTO.valores.map(v => `- ${v}`).join('\n')}

ESTRUCTURA ACTUAL:
- Gerente General: ${EMPRESA_CONTEXTO.estructura.gerencias[0].nombre}
- Gerente Comercial: ${EMPRESA_CONTEXTO.estructura.gerencias[2].nombre}
- Gerente de RRHH: ${EMPRESA_CONTEXTO.estructura.gerencias[4].nombre}
- Gerente de Operaciones: ${EMPRESA_CONTEXTO.estructura.gerencias[3].nombre}

DATOS FINANCIEROS (2025):
- Ingresos: ${EMPRESA_CONTEXTO.financieros.ingresos2025}
- Utilidad neta: ${EMPRESA_CONTEXTO.financieros.utilidad2025}
- Margen neto: ${EMPRESA_CONTEXTO.financieros.margenNeto}

Responde siempre contextualizando tu respuesta a ANDINA FOODS.
Usa nombres reales de los directivos cuando corresponda.
Mantén coherencia con estructura, procesos y políticas de la empresa.
`;

export default EMPRESA_CONTEXTO;
