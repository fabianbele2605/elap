import React, { useEffect, useState } from 'react';
import { X, Download, Printer, RefreshCw } from 'lucide-react';
import './ReportModal.css';

interface ReportModalProps {
  isOpen: boolean;
  onClose: () => void;
  htmlContent: string;
  reportTitle: string;
  agentName: string;
}

export function ReportModal({
  isOpen,
  onClose,
  htmlContent,
  reportTitle,
  agentName
}: ReportModalProps) {
  const [iframeKey, setIframeKey] = useState(0);

  if (!isOpen) return null;

  const handlePrint = () => {
    const iframe = document.getElementById('report-iframe') as HTMLIFrameElement;
    if (iframe && iframe.contentWindow) {
      iframe.contentWindow.print();
    }
  };

  const handleDownloadPDF = () => {
    // Trigger browser's save as PDF (Ctrl+P internally)
    const iframe = document.getElementById('report-iframe') as HTMLIFrameElement;
    if (iframe && iframe.contentWindow) {
      iframe.contentWindow.print();
    }
  };

  const handleRefresh = () => {
    // Force iframe to reload
    setIframeKey(prev => prev + 1);
  };

  // Create blob URL for the HTML content
  const blobUrl = React.useMemo(() => {
    if (!htmlContent) return '';
    const blob = new Blob([htmlContent], { type: 'text/html' });
    return URL.createObjectURL(blob);
  }, [htmlContent]);

  return (
    <div className="report-modal-overlay" onClick={onClose}>
      <div className="report-modal-container" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="report-modal-header">
          <div className="report-modal-title">
            <h2>{reportTitle}</h2>
            <p className="report-agent-name">Generado por: {agentName}</p>
          </div>
          <div className="report-modal-actions">
            <button
              onClick={handleRefresh}
              className="report-modal-btn report-modal-btn-secondary"
              title="Actualizar reporte"
            >
              <RefreshCw size={18} />
            </button>
            <button
              onClick={handleDownloadPDF}
              className="report-modal-btn report-modal-btn-secondary"
              title="Descargar como PDF (Ctrl+P)"
            >
              <Download size={18} />
            </button>
            <button
              onClick={handlePrint}
              className="report-modal-btn report-modal-btn-secondary"
              title="Imprimir"
            >
              <Printer size={18} />
            </button>
            <button
              onClick={onClose}
              className="report-modal-btn report-modal-btn-close"
              title="Cerrar"
            >
              <X size={20} />
            </button>
          </div>
        </div>

        {/* Content - Iframe */}
        <div className="report-modal-content">
          {htmlContent ? (
            <iframe
              key={iframeKey}
              id="report-iframe"
              srcDoc={htmlContent}
              className="report-iframe"
              title={reportTitle}
            />
          ) : (
            <div className="report-modal-empty">
              <p>No hay contenido de reporte disponible</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="report-modal-footer">
          <p className="report-modal-help">
            💡 Tip: Presiona <kbd>Ctrl+P</kbd> para guardar como PDF desde el navegador interno
          </p>
          <button
            onClick={onClose}
            className="report-modal-btn report-modal-btn-primary"
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>
  );
}
