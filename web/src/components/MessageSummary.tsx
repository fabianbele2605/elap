import React from 'react';
import { ChevronRight, Sparkles } from 'lucide-react';

interface MessageSummaryProps {
  text: string;
  maxLines?: number;
  onViewFull?: () => void;
  isLoading?: boolean;
}

/**
 * MessageSummary - Muestra solo un resumen corto del mensaje (3 líneas)
 * Las líneas completas, tablas y métricas van al reporte modal
 * Este componente mantiene el chat limpio y conciso
 */
export const MessageSummary: React.FC<MessageSummaryProps> = ({
  text,
  maxLines = 3,
  onViewFull,
  isLoading = false
}) => {
  // Split en párrafos
  const paragraphs = text.split('\n\n').filter(p => p.trim());

  // Tomar primeros maxLines párrafos para mostrar
  const summary = paragraphs.slice(0, maxLines).join('\n\n');

  // Verificar si hay más contenido (tablas, métricas, análisis)
  const hasMore = paragraphs.length > maxLines;

  return (
    <div className="space-y-2">
      {/* Resumen corto - solo las primeras líneas */}
      <p className="text-slate-700 text-sm leading-relaxed whitespace-pre-wrap">
        {summary}
      </p>

      {/* Botón "Ver análisis completo" si hay contenido adicional */}
      {hasMore && onViewFull && (
        <button
          onClick={onViewFull}
          disabled={isLoading}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          title="Ver análisis completo con tablas, gráficos y métricas"
        >
          <Sparkles className="w-3 h-3" />
          {isLoading ? 'Cargando...' : 'Ver análisis completo'}
          <ChevronRight className="w-3.5 h-3.5" />
        </button>
      )}
    </div>
  );
};
