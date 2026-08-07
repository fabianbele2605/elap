/**
 * Tests para useCompanySetup hook (Fase 3)
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useCompanySetup } from '../useCompanySetup';

// Mock fetch
global.fetch = vi.fn();

const mockCompanyConfig = {
  nombreEmpresa: 'Test Company',
  sector: 'Tecnología',
  ubicacion: 'Bogotá',
  anoFundacion: 2020,
  website: 'https://test.com',
  numEmpleados: 150,
  departamentos: ['RRHH', 'Finanzas'],
  ceo: 'Juan Perez',
  contactoRRHH: 'maria@test.com',
  productos: ['Producto A'],
  servicios: ['Servicio A'],
  clientesPrincipales: 'Grandes empresas',
  salarioPromedio: 3500000,
  presupuestoAnual: 500000000,
  crecimientoEsperado: '15-20%',
  confirmacion: true,
};

describe('useCompanySetup', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('debe inicializar con estado correcto', () => {
    const { result } = renderHook(() => useCompanySetup());

    expect(result.current.status.status).toBe('idle');
    expect(result.current.status.documentsGenerated).toBe(0);
    expect(result.current.config).toEqual({});
  });

  it('debe manejar respuesta exitosa de setup', async () => {
    const { result } = renderHook(() => useCompanySetup());

    // Mock respuesta exitosa
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        company_id: 'test_123',
        status: 'pending',
      }),
    });

    // Mock status response
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        status: 'completed',
        documents_generated: 15,
      }),
    });

    await result.current.generateDocuments(mockCompanyConfig);

    await waitFor(() => {
      expect(result.current.status.status).toBe('completed');
      expect(result.current.status.documentsGenerated).toBe(15);
    });
  });

  it('debe manejar errores de setup', async () => {
    const { result } = renderHook(() => useCompanySetup());

    // Mock error
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 500,
    });

    await result.current.generateDocuments(mockCompanyConfig);

    await waitFor(() => {
      expect(result.current.status.status).toBe('error');
      expect(result.current.status.error).toBeDefined();
    });
  });

  it('debe hacer polling hasta completar', async () => {
    const { result } = renderHook(() => useCompanySetup());

    // Mock setup exitoso
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ company_id: 'test_123' }),
    });

    // Mock status responses (generating → completed)
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        status: 'generating',
        documents_generated: 5,
      }),
    });

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        status: 'completed',
        documents_generated: 15,
      }),
    });

    await result.current.generateDocuments(mockCompanyConfig);

    await waitFor(() => {
      expect(result.current.status.status).toBe('completed');
      expect(result.current.status.documentsGenerated).toBe(15);
    });
  });

  it('debe mostrar mensaje de timeout si tarda demasiado', async () => {
    const { result } = renderHook(() => useCompanySetup());

    // Mock setup exitoso
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ company_id: 'test_123' }),
    });

    // Mock status nunca completado (siempre generating)
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => ({
        status: 'generating',
        documents_generated: 5,
      }),
    });

    await result.current.generateDocuments(mockCompanyConfig);

    await waitFor(
      () => {
        expect(result.current.status.status).toBe('error');
        expect(result.current.status.error).toContain('Timeout');
      },
      { timeout: 5000 }
    );
  }, 10000);

  it('debe usar backoff exponencial en polling', async () => {
    const { result } = renderHook(() => useCompanySetup());

    // Mock setup
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ company_id: 'test_123' }),
    });

    // Mock múltiples polls
    for (let i = 0; i < 5; i++) {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          status: i === 4 ? 'completed' : 'generating',
          documents_generated: (i + 1) * 3,
        }),
      });
    }

    await result.current.generateDocuments(mockCompanyConfig);

    await waitFor(() => {
      expect(result.current.status.status).toBe('completed');
    });

    // Verificar que se hicieron múltiples llamadas fetch
    expect(global.fetch).toHaveBeenCalledTimes(6); // 1 setup + 5 polls
  });

  it('debe manejar 404 del status endpoint', async () => {
    const { result } = renderHook(() => useCompanySetup());

    // Mock setup
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ company_id: 'test_123' }),
    });

    // Mock 404 (generación aún no iniciada)
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 404,
    });

    // Luego completado
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        status: 'completed',
        documents_generated: 15,
      }),
    });

    await result.current.generateDocuments(mockCompanyConfig);

    await waitFor(() => {
      expect(result.current.status.status).toBe('completed');
    });
  });

  it('debe usar el ID de empresa del servidor', async () => {
    const { result } = renderHook(() => useCompanySetup());

    const customCompanyId = 'custom_id_xyz';

    // Mock setup con ID personalizado
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        company_id: customCompanyId,
      }),
    });

    // Mock status
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        status: 'completed',
        documents_generated: 15,
      }),
    });

    await result.current.generateDocuments(mockCompanyConfig);

    await waitFor(() => {
      expect(result.current.status.status).toBe('completed');
    });

    // Verificar que usa el ID correcto en la URL del status
    const statusCall = (global.fetch as any).mock.calls.find(
      (call) => call[0].includes('/status')
    );
    expect(statusCall[0]).toContain(customCompanyId);
  });

  it('debe manejar errores de red en polling', async () => {
    const { result } = renderHook(() => useCompanySetup());

    // Mock setup
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ company_id: 'test_123' }),
    });

    // Mock error de red, luego éxito
    (global.fetch as any).mockRejectedValueOnce(new Error('Network error'));

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        status: 'completed',
        documents_generated: 15,
      }),
    });

    await result.current.generateDocuments(mockCompanyConfig);

    await waitFor(() => {
      expect(result.current.status.status).toBe('completed');
    });
  });
});
