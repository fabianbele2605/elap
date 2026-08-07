/**
 * Tests para GenerationProgress component
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { GenerationProgress } from '../GenerationProgress';

const mockDocuments = [
  {
    id: 'doc_001',
    title: 'Manual del Empleado',
    status: 'ready' as const,
    progress: 100,
  },
  {
    id: 'doc_002',
    title: 'Política de Vacaciones',
    status: 'generating' as const,
    progress: 50,
  },
  {
    id: 'doc_003',
    title: 'Código de Conducta',
    status: 'pending' as const,
    progress: 0,
  },
];

describe('GenerationProgress', () => {
  it('debe renderizar con estado generando', () => {
    render(
      <GenerationProgress
        isGenerating={true}
        documents={mockDocuments}
        totalDocuments={15}
        estimatedTime="2-3 minutos"
      />
    );

    expect(screen.getByText(/Generando Knowledge Pack/i)).toBeInTheDocument();
    expect(screen.getByText(/2-3 minutos/i)).toBeInTheDocument();
  });

  it('debe mostrar progreso correcto', () => {
    render(
      <GenerationProgress
        isGenerating={true}
        documents={mockDocuments}
        totalDocuments={3}
      />
    );

    // 1 completado de 3 = 33%
    expect(screen.getByText(/33%/)).toBeInTheDocument();
  });

  it('debe mostrar estadísticas correctas', () => {
    render(
      <GenerationProgress
        isGenerating={true}
        documents={mockDocuments}
        totalDocuments={15}
      />
    );

    // Completados: 1, En progreso: 1, Pendientes: 1
    expect(screen.getByText('1')).toBeInTheDocument(); // Aparece múltiples veces
  });

  it('debe renderizar todos los documentos', () => {
    render(
      <GenerationProgress
        isGenerating={true}
        documents={mockDocuments}
        totalDocuments={3}
      />
    );

    expect(screen.getByText('Manual del Empleado')).toBeInTheDocument();
    expect(screen.getByText('Política de Vacaciones')).toBeInTheDocument();
    expect(screen.getByText('Código de Conducta')).toBeInTheDocument();
  });

  it('debe mostrar estado de finalización', () => {
    const completedDocs = mockDocuments.map((doc) => ({
      ...doc,
      status: 'ready' as const,
      progress: 100,
    }));

    const { rerender } = render(
      <GenerationProgress
        isGenerating={true}
        documents={completedDocs}
        totalDocuments={3}
      />
    );

    // Redibujar con isGenerating=false
    rerender(
      <GenerationProgress
        isGenerating={false}
        documents={completedDocs}
        totalDocuments={3}
      />
    );

    expect(screen.getByText(/¡Documentos generados exitosamente!/i)).toBeInTheDocument();
  });

  it('debe llamar onComplete cuando termina', () => {
    const onComplete = vi.fn();

    const completedDocs = mockDocuments.map((doc) => ({
      ...doc,
      status: 'ready' as const,
      progress: 100,
    }));

    render(
      <GenerationProgress
        isGenerating={false}
        documents={completedDocs}
        totalDocuments={3}
        onComplete={onComplete}
      />
    );

    // Esperar que onComplete sea llamado
    expect(onComplete).toHaveBeenCalled();
  });

  it('debe mostrar barra de progreso', () => {
    const { container } = render(
      <GenerationProgress
        isGenerating={true}
        documents={mockDocuments}
        totalDocuments={15}
      />
    );

    // Buscar elemento con atributo style que muestre el progreso
    const progressBar = container.querySelector('[style*="width"]');
    expect(progressBar).toBeInTheDocument();
  });

  it('debe manejar lista vacía de documentos', () => {
    render(
      <GenerationProgress
        isGenerating={false}
        documents={[]}
        totalDocuments={15}
      />
    );

    expect(screen.getByText(/Documentos/i)).toBeInTheDocument();
  });

  it('debe mostrar badges de estado correctos', () => {
    render(
      <GenerationProgress
        isGenerating={true}
        documents={mockDocuments}
        totalDocuments={15}
      />
    );

    expect(screen.getByText('Listo')).toBeInTheDocument();
    expect(screen.getByText('Generando')).toBeInTheDocument();
    expect(screen.getByText('Pendiente')).toBeInTheDocument();
  });

  it('debe mostrar botón cancelar cuando está generando', () => {
    const onCancel = vi.fn();

    render(
      <GenerationProgress
        isGenerating={true}
        documents={mockDocuments}
        totalDocuments={15}
        onCancel={onCancel}
      />
    );

    const cancelButton = screen.getByText(/Cancelar Generación/);
    expect(cancelButton).toBeInTheDocument();

    cancelButton.click();
    expect(onCancel).toHaveBeenCalled();
  });

  it('debe mostrar ir al dashboard cuando completa', () => {
    const onComplete = vi.fn();

    const completedDocs = mockDocuments.map((doc) => ({
      ...doc,
      status: 'ready' as const,
      progress: 100,
    }));

    render(
      <GenerationProgress
        isGenerating={false}
        documents={completedDocs}
        totalDocuments={3}
        onComplete={onComplete}
      />
    );

    const dashboardButton = screen.getByText(/Ir al Dashboard/);
    expect(dashboardButton).toBeInTheDocument();
  });
});
