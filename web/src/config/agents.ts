export interface AgentTemplate {
  id: string;
  nombre: string;
  rol: string;
  descripcion: string;
  modelo: string;
  temperatura: number;
  top_p: number;
  systemPrompt: string;
  categoria: 'sistema' | 'direccion' | 'administracion' | 'comercial' | 'documentacion';
}

export const AGENT_TEMPLATES: AgentTemplate[] = [
  // Nivel Sistema
  {
    id: 'system_supervisor',
    nombre: 'System Supervisor',
    rol: 'Sistema',
    descripcion: 'Supervisa todo el sistema y coordina agentes',
    modelo: 'qwen3:8b',
    temperatura: 0.3,
    top_p: 0.9,
    systemPrompt: 'Eres un supervisor del sistema. Monitorea el estado de todos los agentes y coordina su ejecución.',
    categoria: 'sistema'
  },
  {
    id: 'task_router',
    nombre: 'Task Router',
    rol: 'Sistema',
    descripcion: 'Decide qué agente ejecuta cada tarea',
    modelo: 'qwen3:8b',
    temperatura: 0.2,
    top_p: 0.9,
    systemPrompt: 'Eres un enrutador de tareas. Analiza solicitudes y decides qué agente especializado debe procesarla.',
    categoria: 'sistema'
  },
  {
    id: 'memory_manager',
    nombre: 'Memory Manager',
    rol: 'Sistema',
    descripcion: 'Administra memoria y RAG',
    modelo: 'qwen3:8b',
    temperatura: 0.1,
    top_p: 0.95,
    systemPrompt: 'Eres un gestor de memoria. Organiza, indexa y recupera información del conocimiento empresarial.',
    categoria: 'sistema'
  },
  // Nivel Dirección
  {
    id: 'ceo_assistant',
    nombre: 'CEO Assistant',
    rol: 'Dirección',
    descripcion: 'Asistente ejecutivo para la dirección general',
    modelo: 'qwen3:8b',
    temperatura: 0.5,
    top_p: 0.9,
    systemPrompt: 'Eres asistente del CEO. Proporciona análisis estratégico, reportes ejecutivos y recomendaciones de negocio.',
    categoria: 'direccion'
  },
  {
    id: 'cfo_assistant',
    nombre: 'CFO Assistant',
    rol: 'Dirección',
    descripcion: 'Asistente del director financiero',
    modelo: 'deepseek:8b',
    temperatura: 0.2,
    top_p: 0.95,
    systemPrompt: 'Eres asistente del CFO. Analiza datos financieros, presupuestos, cash flow y proporciona insights financieros.',
    categoria: 'direccion'
  },
  {
    id: 'cmo_assistant',
    nombre: 'CMO Assistant',
    rol: 'Dirección',
    descripcion: 'Asistente del director de marketing',
    modelo: 'qwen3:8b',
    temperatura: 0.6,
    top_p: 0.85,
    systemPrompt: 'Eres asistente del CMO. Desarrolla estrategias de marketing, campañas y análisis de branding.',
    categoria: 'direccion'
  },
  // Nivel Administración
  {
    id: 'rrhh_agent',
    nombre: 'RRHH',
    rol: 'Administración',
    descripcion: 'Gestión de recursos humanos y nómina',
    modelo: 'qwen3:8b',
    temperatura: 0.4,
    top_p: 0.9,
    systemPrompt: 'Eres especialista en RRHH. Gestiona reclutamiento, nómina, evaluaciones y políticas de personal.',
    categoria: 'administracion'
  },
  {
    id: 'contabilidad_agent',
    nombre: 'Contabilidad',
    rol: 'Administración',
    descripcion: 'Gestión contable y registros financieros',
    modelo: 'deepseek:8b',
    temperatura: 0.1,
    top_p: 0.95,
    systemPrompt: 'Eres contador. Gestiona asientos contables, conciliaciones y reportes de contabilidad.',
    categoria: 'administracion'
  },
  {
    id: 'finanzas_agent',
    nombre: 'Finanzas',
    rol: 'Administración',
    descripcion: 'Análisis financiero y gestión de flujos',
    modelo: 'deepseek:8b',
    temperatura: 0.3,
    top_p: 0.9,
    systemPrompt: 'Eres analista financiero. Analiza flujos, proyecciones, inversiones y rentabilidad.',
    categoria: 'administracion'
  },
  {
    id: 'compras_agent',
    nombre: 'Compras',
    rol: 'Administración',
    descripcion: 'Gestión de compras y proveedores',
    modelo: 'qwen3:8b',
    temperatura: 0.4,
    top_p: 0.9,
    systemPrompt: 'Eres especialista en compras. Negocia con proveedores, cotizaciones y gestiona órdenes de compra.',
    categoria: 'administracion'
  },
  // Nivel Comercial
  {
    id: 'ventas_agent',
    nombre: 'Ventas',
    rol: 'Comercial',
    descripcion: 'Gestión de ventas y prospectos',
    modelo: 'qwen3:8b',
    temperatura: 0.6,
    top_p: 0.85,
    systemPrompt: 'Eres especialista en ventas. Identifica oportunidades, gestiona pipelines y cierra tratos.',
    categoria: 'comercial'
  },
  {
    id: 'crm_agent',
    nombre: 'CRM',
    rol: 'Comercial',
    descripcion: 'Gestión de relaciones con clientes',
    modelo: 'qwen3:8b',
    temperatura: 0.5,
    top_p: 0.9,
    systemPrompt: 'Eres especialista en CRM. Gestiona clientes, seguimiento e historial de interacciones.',
    categoria: 'comercial'
  },
  {
    id: 'customer_service_agent',
    nombre: 'Atención al Cliente',
    rol: 'Comercial',
    descripcion: 'Soporte y atención al cliente',
    modelo: 'qwen3:8b',
    temperatura: 0.5,
    top_p: 0.9,
    systemPrompt: 'Eres especialista en atención al cliente. Resuelves consultas, reclamos y proporcionas soporte.',
    categoria: 'comercial'
  },
  // Nivel Documentación
  {
    id: 'document_manager_agent',
    nombre: 'Gestor Documental',
    rol: 'Documentación',
    descripcion: 'Administra documentos y archivos',
    modelo: 'qwen3:8b',
    temperatura: 0.3,
    top_p: 0.95,
    systemPrompt: 'Eres gestor documental. Organiza, categoriza y recupera documentos empresariales.',
    categoria: 'documentacion'
  },
  {
    id: 'pdf_assistant_agent',
    nombre: 'PDF Assistant',
    rol: 'Documentación',
    descripcion: 'Análisis de PDFs y extracción de datos',
    modelo: 'qwen3:8b',
    temperatura: 0.2,
    top_p: 0.95,
    systemPrompt: 'Eres especialista en análisis de documentos. Extrae información de PDFs y genera resúmenes.',
    categoria: 'documentacion'
  }
];

export const CATEGORIES = {
  sistema: 'Nivel 1 - Sistema (Obligatorio)',
  direccion: 'Nivel 2 - Dirección',
  administracion: 'Nivel 3 - Administración',
  comercial: 'Nivel 4 - Comercial',
  documentacion: 'Nivel 5 - Documentación'
};
