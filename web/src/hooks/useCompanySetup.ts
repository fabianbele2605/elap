import { useState } from 'react';

interface CompanyConfig {
  nombreEmpresa: string;
  sector: string;
  ubicacion: string;
  anoFundacion: number;
  website?: string;
  numEmpleados: number;
  departamentos: string[];
  ceo?: string;
  contactoRRHH?: string;
  productos: string[];
  servicios: string[];
  clientesPrincipales?: string;
  salarioPromedio: number;
  presupuestoAnual?: number;
  crecimientoEsperado?: string;
}

interface GenerationStatus {
  status: 'idle' | 'generating' | 'completed' | 'error';
  documentsGenerated: number;
  message: string;
  estimatedTime?: string;
  error?: string;
}

export function useCompanySetup() {
  const [config, setConfig] = useState<Partial<CompanyConfig>>({});
  const [status, setStatus] = useState<GenerationStatus>({
    status: 'idle',
    documentsGenerated: 0,
    message: '',
  });

  const generateDocuments = async (fullConfig: CompanyConfig) => {
    setStatus({
      status: 'generating',
      documentsGenerated: 0,
      message: 'Generando 15 documentos profesionales...',
      estimatedTime: '2-3 minutos',
    });

    try {
      // Step 1: Send configuration to Rust backend
      // Rust will forward to Python gRPC
      const setupResponse = await fetch('http://localhost:5000/company/setup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(fullConfig),
      });

      if (!setupResponse.ok) {
        throw new Error(`Error en configuración de empresa: ${setupResponse.status}`);
      }

      const setupData = await setupResponse.json();
      const companyId = setupData.company_id || fullConfig.nombreEmpresa.replace(/\s+/g, '_');

      // Step 2: Poll for status with exponential backoff
      let attempts = 0;
      const maxAttempts = 120; // 120 * 1s = 2 minutes max
      let backoffMs = 500; // Start with 500ms

      const pollStatus = async (): Promise<void> => {
        if (attempts >= maxAttempts) {
          throw new Error('Timeout: documentos tardaron más de 2 minutos');
        }

        attempts++;

        try {
          // Fetch real status from backend
          const statusResponse = await fetch(
            `http://localhost:5000/company/${companyId}/status`,
            {
              method: 'GET',
              headers: { 'Content-Type': 'application/json' },
            }
          );

          if (statusResponse.ok) {
            const statusData = await statusResponse.json();

            // Update UI with latest status
            const completedDocs = statusData.documents_generated || 0;
            setStatus({
              status: statusData.status === 'completed' ? 'completed' : 'generating',
              documentsGenerated: completedDocs,
              message:
                statusData.status === 'completed'
                  ? `¡${completedDocs} documentos generados exitosamente!`
                  : `Generando documentos... ${completedDocs}/15 completados`,
            });

            // If completed, stop polling
            if (statusData.status === 'completed') {
              return;
            }
          } else if (statusResponse.status === 404) {
            // Generación aún no iniciada, esperar
            setStatus((prev) => ({
              ...prev,
              message: 'Iniciando generación de documentos...',
            }));
          } else {
            throw new Error(`Error obteniendo estado: ${statusResponse.status}`);
          }
        } catch (fetchErr) {
          // Log pero continúa intentando (el servidor podría estar ocupado)
          console.warn(`Poll attempt ${attempts} failed:`, fetchErr);
        }

        // Wait with exponential backoff (max 3 seconds)
        const waitTime = Math.min(backoffMs, 3000);
        backoffMs = Math.min(backoffMs * 1.2, 3000);

        await new Promise((resolve) => setTimeout(resolve, waitTime));
        await pollStatus();
      };

      await pollStatus();
    } catch (err) {
      setStatus({
        status: 'error',
        documentsGenerated: 0,
        message: 'Error generando documentos',
        error: err instanceof Error ? err.message : 'Error desconocido',
      });
    }
  };

  return {
    config,
    status,
    generateDocuments,
  };
}
