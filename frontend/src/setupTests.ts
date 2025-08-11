// Setup para React Testing Library
import '@testing-library/jest-dom';

// Setup global para tests
global.ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));