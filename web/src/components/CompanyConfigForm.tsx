import React, { useState } from 'react';
import { ChevronRight, ChevronLeft, CheckCircle } from 'lucide-react';

interface CompanyConfig {
  // Step 1: General
  nombreEmpresa: string;
  sector: string;
  ubicacion: string;
  anoFundacion: number;
  website?: string;

  // Step 2: Organization
  numEmpleados: number;
  departamentos: string[];
  ceo?: string;
  contactoRRHH?: string;

  // Step 3: Products/Services
  productos: string[];
  servicios: string[];
  clientesPrincipales?: string;

  // Step 4: Financial
  salarioPromedio: number;
  presupuestoAnual?: number;
  crecimientoEsperado?: string;

  // Step 5: Confirmation
  confirmacion: boolean;
}

interface CompanyConfigFormProps {
  onComplete?: (config: CompanyConfig) => void;
}

const SECTORES = [
  'Alimentos y Bebidas',
  'Tecnología',
  'Financiero',
  'Salud',
  'Educación',
  'Manufactura',
  'Retail',
  'Servicios',
  'Consultoría',
  'Otro',
];

const DEPARTAMENTOS_COMUNES = [
  'RRHH',
  'Finanzas',
  'Operaciones',
  'Ventas',
  'Marketing',
  'IT',
  'Legal',
  'Contabilidad',
];

export const CompanyConfigForm: React.FC<CompanyConfigFormProps> = ({
  onComplete,
}) => {
  const [step, setStep] = useState(1);
  const [config, setConfig] = useState<Partial<CompanyConfig>>({
    departamentos: ['RRHH', 'Finanzas', 'Operaciones'],
  });

  const handleInputChange = (field: string, value: any) => {
    setConfig((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleNext = () => {
    if (step < 5) setStep(step + 1);
    else if (onComplete && config.confirmacion) {
      onComplete(config as CompanyConfig);
    }
  };

  const handlePrev = () => {
    if (step > 1) setStep(step - 1);
  };

  const toggleDepartment = (dept: string) => {
    setConfig((prev) => {
      const depts = prev.departamentos || [];
      const updated = depts.includes(dept)
        ? depts.filter((d) => d !== dept)
        : [...depts, dept];
      return { ...prev, departamentos: updated };
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-8">
      <div className="max-w-2xl mx-auto">
        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-3xl font-bold text-slate-900">
              Configuración de Empresa
            </h1>
            <span className="text-sm font-medium text-slate-600">
              Paso {step} de 5
            </span>
          </div>
          <div className="w-full h-2 bg-slate-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-600 transition-all duration-300"
              style={{ width: `${(step / 5) * 100}%` }}
            />
          </div>
        </div>

        {/* Form Content */}
        <div className="bg-white rounded-lg shadow-lg p-8">
          {/* Step 1: General Info */}
          {step === 1 && (
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-slate-900 mb-6">
                Información General
              </h2>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Nombre de la Empresa *
                </label>
                <input
                  type="text"
                  value={config.nombreEmpresa || ''}
                  onChange={(e) => handleInputChange('nombreEmpresa', e.target.value)}
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Ej: Andina Foods"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Sector Empresarial *
                </label>
                <select
                  value={config.sector || ''}
                  onChange={(e) => handleInputChange('sector', e.target.value)}
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Selecciona un sector</option>
                  {SECTORES.map((s) => (
                    <option key={s} value={s}>
                      {s}
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Ubicación *
                  </label>
                  <input
                    type="text"
                    value={config.ubicacion || ''}
                    onChange={(e) => handleInputChange('ubicacion', e.target.value)}
                    placeholder="Ej: Bogotá, Colombia"
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Año de Fundación
                  </label>
                  <input
                    type="number"
                    value={config.anoFundacion || ''}
                    onChange={(e) => handleInputChange('anoFundacion', parseInt(e.target.value))}
                    placeholder="2020"
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Website
                </label>
                <input
                  type="url"
                  value={config.website || ''}
                  onChange={(e) => handleInputChange('website', e.target.value)}
                  placeholder="https://ejemplo.com"
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          )}

          {/* Step 2: Organization */}
          {step === 2 && (
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-slate-900 mb-6">
                Estructura Organizacional
              </h2>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Número de Empleados *
                </label>
                <input
                  type="number"
                  value={config.numEmpleados || ''}
                  onChange={(e) => handleInputChange('numEmpleados', parseInt(e.target.value))}
                  placeholder="50"
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Departamentos
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {DEPARTAMENTOS_COMUNES.map((dept) => (
                    <label key={dept} className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={config.departamentos?.includes(dept) || false}
                        onChange={() => toggleDepartment(dept)}
                        className="h-4 w-4"
                      />
                      <span className="text-sm text-slate-700">{dept}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    CEO / Gerente General
                  </label>
                  <input
                    type="text"
                    value={config.ceo || ''}
                    onChange={(e) => handleInputChange('ceo', e.target.value)}
                    placeholder="Nombre"
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Contacto RRHH
                  </label>
                  <input
                    type="text"
                    value={config.contactoRRHH || ''}
                    onChange={(e) => handleInputChange('contactoRRHH', e.target.value)}
                    placeholder="Nombre / Email"
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Step 3: Products/Services */}
          {step === 3 && (
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-slate-900 mb-6">
                Productos y Servicios
              </h2>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Productos Principales (separados por coma)
                </label>
                <textarea
                  value={config.productos?.join(', ') || ''}
                  onChange={(e) =>
                    handleInputChange(
                      'productos',
                      e.target.value.split(',').map((s) => s.trim())
                    )
                  }
                  placeholder="Ej: Arroz, Aceite, Harina"
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 h-24 resize-none"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Servicios Ofrecidos (separados por coma)
                </label>
                <textarea
                  value={config.servicios?.join(', ') || ''}
                  onChange={(e) =>
                    handleInputChange(
                      'servicios',
                      e.target.value.split(',').map((s) => s.trim())
                    )
                  }
                  placeholder="Ej: Distribución, Asesoría, Consultoría"
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 h-24 resize-none"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Clientes Principales
                </label>
                <input
                  type="text"
                  value={config.clientesPrincipales || ''}
                  onChange={(e) => handleInputChange('clientesPrincipales', e.target.value)}
                  placeholder="Ej: Cadenas de retail, Distribuidores"
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          )}

          {/* Step 4: Financial */}
          {step === 4 && (
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-slate-900 mb-6">
                Información Financiera
              </h2>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Salario Promedio (COP) *
                </label>
                <input
                  type="number"
                  value={config.salarioPromedio || ''}
                  onChange={(e) => handleInputChange('salarioPromedio', parseInt(e.target.value))}
                  placeholder="3000000"
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Presupuesto Anual (COP)
                </label>
                <input
                  type="number"
                  value={config.presupuestoAnual || ''}
                  onChange={(e) => handleInputChange('presupuestoAnual', parseInt(e.target.value))}
                  placeholder="500000000"
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Crecimiento Esperado (Anual)
                </label>
                <select
                  value={config.crecimientoEsperado || ''}
                  onChange={(e) => handleInputChange('crecimientoEsperado', e.target.value)}
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Selecciona un rango</option>
                  <option value="0-10%">0-10%</option>
                  <option value="10-20%">10-20%</option>
                  <option value="20-50%">20-50%</option>
                  <option value="50%+">50%+</option>
                </select>
              </div>
            </div>
          )}

          {/* Step 5: Confirmation */}
          {step === 5 && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-slate-900 mb-6">
                Confirmación
              </h2>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 space-y-3">
                <div className="flex items-start gap-3">
                  <CheckCircle className="h-6 w-6 text-green-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="font-medium text-slate-900">
                      {config.nombreEmpresa}
                    </p>
                    <p className="text-sm text-slate-600">
                      {config.sector} • {config.ubicacion} • {config.numEmpleados} empleados
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                <h3 className="font-medium text-slate-900 mb-2">
                  El sistema generará:
                </h3>
                <ul className="text-sm text-slate-700 space-y-1 list-disc list-inside">
                  <li>5 documentos de RRHH (políticas, manual, etc.)</li>
                  <li>3 documentos de Finanzas (presupuesto, reportes)</li>
                  <li>4 documentos de Operaciones (procesos, procedimientos)</li>
                  <li>2 documentos Legal (términos, cumplimiento)</li>
                  <li>1 documento de Ventas (estrategia comercial)</li>
                </ul>
                <p className="text-sm text-amber-700 mt-3">
                  ⏱️ Esto tomará aproximadamente 2-3 minutos.
                </p>
              </div>

              <label className="flex items-center gap-3">
                <input
                  type="checkbox"
                  checked={config.confirmacion || false}
                  onChange={(e) => handleInputChange('confirmacion', e.target.checked)}
                  className="h-4 w-4"
                />
                <span className="text-sm text-slate-700">
                  Confirmo que la información es correcta y autorizo la generación de documentos
                </span>
              </label>
            </div>
          )}

          {/* Buttons */}
          <div className="flex items-center justify-between mt-8">
            <button
              onClick={handlePrev}
              disabled={step === 1}
              className="flex items-center gap-2 px-4 py-2 text-slate-700 border border-slate-300 rounded-lg hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronLeft className="h-4 w-4" />
              Anterior
            </button>

            <span className="text-sm text-slate-600">
              Paso {step} de 5
            </span>

            <button
              onClick={handleNext}
              disabled={step < 5 && !isStepComplete(step, config)}
              className="flex items-center gap-2 px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-400 text-white rounded-lg disabled:cursor-not-allowed transition-colors"
            >
              {step === 5 ? 'Generar Documentos' : 'Siguiente'}
              {step < 5 && <ChevronRight className="h-4 w-4" />}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

function isStepComplete(step: number, config: Partial<CompanyConfig>): boolean {
  switch (step) {
    case 1:
      return !!(config.nombreEmpresa && config.sector && config.ubicacion);
    case 2:
      return !!(config.numEmpleados && config.departamentos?.length);
    case 3:
      return !!(config.productos?.length && config.servicios?.length);
    case 4:
      return !!config.salarioPromedio;
    case 5:
      return true;
    default:
      return false;
  }
}
