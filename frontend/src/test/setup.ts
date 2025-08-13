// Mock de import.meta para Jest
Object.defineProperty(global, 'import', {
  value: {
    meta: {
      env: {
        VITE_API_BASE_URL: 'http://localhost:8000',
        VITE_BUILD_NUMBER: '1',
        MODE: 'test'
      }
    }
  }
});
