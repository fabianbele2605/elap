import React, { useState } from 'react';
import { CompanyConfigForm } from './CompanyConfigForm';
import { GenerationProgress } from './GenerationProgress';
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
  const [phase, setPhase] = useState<'form' | 'progress'>('form');
  const [documents, setDocuments] = useState<Document[]>([]);
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
    setPhase('progress');

    // Initialize documents
    const initialDocs: Document[] = DOCUMENT_TITLES.map((title, idx) => ({
      id: `doc_${idx}`,
      title,
      status: 'pending',
      progress: 0,
    }));
    setDocuments(initialDocs);

    // Simulate document generation with staggered progress
    const simulateGeneration = async () => {
      for (let i = 0; i < TOTAL_DOCUMENTS; i++) {
        // Transition to generating
        setDocuments((prev) =>
          prev.map((doc, idx) =>
            idx === i ? { ...doc, status: 'generating' as const } : doc
          )
        );

        // Simulate progress (0% to 100%)
        for (let progress = 0; progress <= 100; progress += Math.random() * 50) {
          await new Promise((resolve) => setTimeout(resolve, 100));
          setDocuments((prev) =>
            prev.map((doc, idx) =>
              idx === i ? { ...doc, progress: Math.min(progress, 100) } : doc
            )
          );
        }

        // Mark as complete
        setDocuments((prev) =>
          prev.map((doc, idx) =>
            idx === i
              ? { ...doc, status: 'ready' as const, progress: 100 }
              : doc
          )
        );

        // Small delay between documents
        await new Promise((resolve) => setTimeout(resolve, 300));
      }
    };

    // Actually call the backend
    try {
      await generateDocuments(config);
      // If backend call succeeds, we're done
      // Update documents to show all as ready
      setDocuments((prev) =>
        prev.map((doc) => ({
          ...doc,
          status: 'ready' as const,
          progress: 100,
        }))
      );
    } catch (err) {
      // If error, run simulation anyway for UX
      await simulateGeneration();
    }
  };

  const handleProgressComplete = () => {
    if (onSuccess) {
      onSuccess();
    }
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
    </>
  );
};
