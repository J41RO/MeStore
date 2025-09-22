// Jest setup file for polyfilling import.meta
// This file runs before any tests and provides import.meta support for Jest

// Set Node.js environment variable for Jest
process.env.NODE_ENV = 'test';

// Mock import.meta for Jest environment
const importMetaMock = {
  env: {
    VITE_API_BASE_URL: 'http://localhost:8000',
    VITE_BUILD_NUMBER: '1',
    MODE: 'test',
    DEV: false,
    PROD: false,
    BASE_URL: '/',
  },
  url: 'file://localhost/test',
  hot: undefined,
  glob: undefined,
};

// Create multiple polyfills to ensure compatibility
if (typeof globalThis !== 'undefined') {
  globalThis.import = { meta: importMetaMock };
}

if (typeof global !== 'undefined') {
  global.import = { meta: importMetaMock };
  global.importMetaMock = importMetaMock;
}

// Create a stub for import.meta that can be used in modules
global.importMeta = importMetaMock;

// Mock localStorage for tests
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock;

// Mock sessionStorage for tests
const sessionStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.sessionStorage = sessionStorageMock;

// Mock window.location for tests
if (!window.location || typeof window.location.assign !== 'function') {
  delete window.location;
  window.location = {
    href: 'http://localhost:3000',
    origin: 'http://localhost:3000',
    protocol: 'http:',
    host: 'localhost:3000',
    hostname: 'localhost',
    port: '3000',
    pathname: '/',
    search: '',
    hash: '',
    assign: jest.fn(),
    replace: jest.fn(),
    reload: jest.fn(),
  };
}

// Mock ResizeObserver for tests
global.ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// Mock IntersectionObserver for tests
global.IntersectionObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// Suppress React Router future flag warnings in tests
const originalConsoleWarn = console.warn;
console.warn = (...args) => {
  if (
    typeof args[0] === 'string' &&
    args[0].includes('React Router Future Flag Warning')
  ) {
    return;
  }
  originalConsoleWarn.apply(console, args);
};