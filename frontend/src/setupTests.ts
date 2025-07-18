// Jest-dom adds custom jest matchers for asserting on DOM nodes
import '@testing-library/jest-dom/jest-globals';

// Mock para IntersectionObserver (común en componentes React)
(global as any).IntersectionObserver = class IntersectionObserver {
  root: Element | null = null;
  rootMargin: string = '';
  thresholds: ReadonlyArray<number> = [];
  
  constructor() {}
  observe() {
    return null;
  }
  disconnect() {
    return null;
  }
  unobserve() {
    return null;
  }
  takeRecords(): IntersectionObserverEntry[] {
    return [];
  }
};

// Mock para window.matchMedia (para responsive components)
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Configuración global para tests
beforeEach(() => {
  // Reset de mocks antes de cada test
  jest.clearAllMocks();
});

// Mock para SVGs globalmente
jest.mock('*.svg', () => 'mocked-svg');
