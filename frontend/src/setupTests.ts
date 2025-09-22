// Import jest-dom matchers
import '@testing-library/jest-dom';
import React from 'react';

// Mock window.matchMedia globalmente para todos los tests
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock WebSocket globally to prevent real connections
global.WebSocket = jest.fn().mockImplementation(() => ({
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
  send: jest.fn(),
  close: jest.fn(),
  readyState: 1, // WebSocket.OPEN
  CONNECTING: 0,
  OPEN: 1,
  CLOSING: 2,
  CLOSED: 3,
}));

// Mock fetch to prevent real HTTP calls
global.fetch = jest.fn().mockImplementation(() =>
  Promise.resolve({
    ok: true,
    status: 200,
    json: () => Promise.resolve({}),
    text: () => Promise.resolve(''),
  })
);

// Mock axios globally with more comprehensive implementation
const mockAxios = {
  create: jest.fn(() => mockAxios),
  get: jest.fn(() => Promise.resolve({ data: {} })),
  post: jest.fn(() => Promise.resolve({ data: {} })),
  put: jest.fn(() => Promise.resolve({ data: {} })),
  delete: jest.fn(() => Promise.resolve({ data: {} })),
  patch: jest.fn(() => Promise.resolve({ data: {} })),
  interceptors: {
    request: { use: jest.fn(), eject: jest.fn() },
    response: { use: jest.fn(), eject: jest.fn() },
  },
  defaults: {
    baseURL: 'http://localhost:8000',
    headers: { 'Content-Type': 'application/json' },
    timeout: 30000,
  },
  isCancel: jest.fn(() => false),
  CancelToken: {
    source: jest.fn(() => ({
      token: {},
      cancel: jest.fn(),
    })),
  },
};

jest.mock('axios', () => ({
  __esModule: true,
  default: mockAxios,
  ...mockAxios,
}));

// Mock Vitest globals for compatibility
global.vi = jest;

// Note: localStorage and sessionStorage are now mocked in jest.setup.js
// to avoid conflicts with import.meta polyfill
