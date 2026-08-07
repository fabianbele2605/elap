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
      // Step 1: Send configuration to backend
      const setupResponse = await fetch('http://localhost:3000/company/setup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(fullConfig),
      });

      if (!setupResponse.ok) {
        throw new Error('Error en configuración de empresa');
      }

      const setupData = await setupResponse.json();

      // Step 2: Poll for status
      let attempts = 0;
      const maxAttempts = 60; // 60 attempts * 2s = 2 minutes max

      const pollStatus = async (): Promise<void> => {
        if (attempts >= maxAttempts) {
          throw new Error('Timeout generando documentos');
        }

        attempts++;

        // Simulate: en producción sería /company/{id}/status
        const statusResponse = await fetch(
          `http://localhost:3000/company/${fullConfig.nombreEmpresa}/status`,
          {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
          }
        );

        if (statusResponse.ok) {
          const statusData = await statusResponse.json();

          if (statusData.status === 'completed') {
            setStatus({
              status: 'completed',
              documentsGenerated: statusData.documents_generated || 15,
              message: `¡${statusData.documents_generated || 15} documentos generados exitosamente!`,
            });
            return;
          }
        }

        // Keep polling
        await new Promise((resolve) => setTimeout(resolve, 2000));
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
