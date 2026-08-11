import { useState, useCallback } from 'react';

export interface Report {
  htmlContent: string;
  title: string;
  agentName: string;
  generatedAt: Date;
}

export function useReport() {
  const [isOpen, setIsOpen] = useState(false);
  const [currentReport, setCurrentReport] = useState<Report | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const openReport = useCallback((report: Report) => {
    setCurrentReport(report);
    setIsOpen(true);
    setError(null);
  }, []);

  const closeReport = useCallback(() => {
    setIsOpen(false);
    // Keep the report in state for potential re-opening
  }, []);

  const generateReport = useCallback(async (
    agentId: string,
    agentName: string,
    reportData: any
  ) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`http://localhost:5000/api/reports/${agentId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(reportData)
      });

      if (!response.ok) {
        throw new Error(`Error generating report: ${response.statusText}`);
      }

      const result = await response.json();

      if (result.status === 'success' && result.html) {
        const report: Report = {
          htmlContent: result.html,
          title: reportData.title || 'Reporte Generado',
          agentName: agentName,
          generatedAt: new Date()
        };

        openReport(report);
        return report;
      } else {
        throw new Error('Failed to generate report');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
      console.error('Report generation error:', err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [openReport]);

  const clearReport = useCallback(() => {
    setCurrentReport(null);
    setError(null);
  }, []);

  return {
    isOpen,
    currentReport,
    isLoading,
    error,
    openReport,
    closeReport,
    generateReport,
    clearReport
  };
}
