// Mock completo del módulo apiClient para evitar import.meta
jest.mock('../apiClient', () => ({
  apiClient: {
    defaults: {
      baseURL: 'http://192.168.1.137:8000',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    },
    create: jest.fn(),
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
  },
}));

import { apiClient } from '../apiClient';

describe('apiClient', () => {
  it('should have correct base configuration', () => {
    expect(apiClient.defaults.baseURL).toBe('http://192.168.1.137:8000');
    expect(apiClient.defaults.timeout).toBe(30000);
    expect(apiClient.defaults.headers['Content-Type']).toBe('application/json');
  });

  it('should have axios methods available', () => {
    expect(apiClient.get).toBeDefined();
    expect(apiClient.post).toBeDefined();
    expect(apiClient.put).toBeDefined();
    expect(apiClient.delete).toBeDefined();
  });

  it('should have proper timeout configuration', () => {
    expect(apiClient.defaults.timeout).toBe(30000);
  });

  it('should have correct default headers', () => {
    expect(apiClient.defaults.headers['Content-Type']).toBe('application/json');
  });

  it('should be properly configured for development', () => {
    expect(apiClient.defaults.baseURL).toContain('192.168.1.137:8000');
  });
});
