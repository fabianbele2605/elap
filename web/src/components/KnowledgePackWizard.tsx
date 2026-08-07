import React, { useState } from 'react';
import { CompanyConfigForm } from './CompanyConfigForm';
import { GenerationProgress } from './GenerationProgress';
import { DocumentsGeneratedDashboard } from './DocumentsGeneratedDashboard';
import { useCompanySetup } from '../hooks/useCompanySetup';

interface Document {
  id: string;
  title: string;
  status: 'pending' | 'generating' | 'ready' | 'error';
  progress: number;
}

interface KnowledgePackWizardProps {
  onSuccess?: () => void;
}

export const KnowledgePackWizard: React.FC<KnowledgePackWizardProps> = ({
  onSuccess,
}) => {
  const [phase, setPhase] = useState<'form' | 'progress' | 'dashboard'>('form');
  const [documents, setDocuments] = useState<Document[]>([]);
  const [companyName, setCompanyName] = useState('');
  const { generateDocuments, status } = useCompanySetup();

  const TOTAL_DOCUMENTS = 15;
  const DOCUMENT_TITLES = [
    'Manual del Empleado',
    'Política de Vacaciones',
    'Código de Conducta',
    'Política de Ausencias',
    'Procedimiento de Contratación',
    'Presupuesto Anual',
    'Política de Gastos',
    'Reportes Financieros',
    'Política de Calidad',
    'Matriz de Procesos',
    'Procedimientos Operacionales',
    'Política de Compras',
    'Términos y Condiciones',
    'Política de Privacidad',
    'Estrategia Comercial',
  ];

  const handleFormComplete = async (config: any) => {
    setCompanyName(config.nombreEmpresa);
    setPhase('progress');

    // Initialize documents
    const initialDocs: Document[] = DOCUMENT_TITLES.map((title, idx) => ({
      id: `doc_${idx}`,
      title,
      status: 'pending',
      progress: 0,
    }));
    setDocuments(initialDocs);

    // Actually call the backend for real generation
    try {
      await generateDocuments(config);
      // If backend call succeeds, update documents to show all as ready
      setDocuments((prev) =>
        prev.map((doc) => ({
          ...doc,
          status: 'ready' as const,
          progress: 100,
        }))
      );
    } catch (err) {
      console.error('Error generating documents:', err);
      // Show error state
      setDocuments((prev) =>
        prev.map((doc) => ({
          ...doc,
          status: 'error' as const,
        }))
      );
    }
  };

  const handleProgressComplete = () => {
    // Transition to dashboard view
    setPhase('dashboard');
  };

  const handleCancel = () => {
    setPhase('form');
    setDocuments([]);
  };

  return (
    <>
      {phase === 'form' && (
        <CompanyConfigForm onComplete={handleFormComplete} />
      )}
      {phase === 'progress' && (
        <GenerationProgress
          isGenerating={status.status === 'generating'}
          documents={documents}
          totalDocuments={TOTAL_DOCUMENTS}
          estimatedTime={status.estimatedTime}
          onCancel={handleCancel}
          onComplete={handleProgressComplete}
        />
      )}
      {phase === 'dashboard' && (
        <DocumentsGeneratedDashboard
          companyName={companyName}
          onDownload={(docId) => {
            console.log('Download:', docId);
            // TODO: Implementar descarga real
          }}
          onPreview={(docId) => {
            console.log('Preview:', docId);
            // TODO: Implementar vista previa
          }}
          onRegenerate={(docId) => {
            console.log('Regenerate:', docId);
            // TODO: Implementar regeneración
          }}
        />
      )}
    </>
  );
};
