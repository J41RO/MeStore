// Test básico del hook useBreadcrumb
import * as React from 'react';
import { renderHook } from '@testing-library/react';
import { BrowserRouter, MemoryRouter } from 'react-router-dom';
import { useBreadcrumb } from '../useBreadcrumb';

const wrapper = ({ children }: { children: React.ReactNode }) => (
  React.createElement(BrowserRouter, null, children)
);

describe('useBreadcrumb', () => {
  it('generates breadcrumbs correctly for root path', () => {
    const { result } = renderHook(() => useBreadcrumb(), { wrapper });
    expect(result.current).toEqual([
      { label: 'Inicio', path: '/', isActive: false }
    ]);
  });

  it('generates breadcrumbs with active state for nested paths', () => {
    // Usar MemoryRouter para simular ruta específica
    const TestWrapper = ({ children }: { children: React.ReactNode }) => (
      React.createElement(MemoryRouter, { initialEntries: ['/productos'] }, children)
    );
    
    const { result } = renderHook(() => useBreadcrumb(), { wrapper: TestWrapper });
    
    expect(result.current).toEqual([
      { label: 'Inicio', path: '/', isActive: false },
      { label: 'Productos', path: '/productos', isActive: true }
    ]);
  });

  it('uses custom labels for known routes', () => {
    // Test con ruta que tiene mapeo personalizado
    const TestWrapper = ({ children }: { children: React.ReactNode }) => (
      React.createElement(MemoryRouter, { initialEntries: ['/dashboard'] }, children)
    );
    
    const { result } = renderHook(() => useBreadcrumb(), { wrapper: TestWrapper });
    
    expect(result.current).toEqual([
      { label: 'Inicio', path: '/', isActive: false },
      { label: 'Panel de Control', path: '/dashboard', isActive: true }
    ]);
  });
});