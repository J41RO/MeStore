// Import.meta polyfill for Jest tests
// Provides import.meta.env support in test environment

declare global {
  namespace NodeJS {
    interface Global {
      import: {
        meta: {
          env: Record<string, any>;
          url: string;
          hot?: any;
          glob?: any;
        };
      };
    }
  }
}

// Mock import.meta object
const importMeta = {
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

// Set up global import.meta
if (typeof globalThis !== 'undefined') {
  (globalThis as any).import = { meta: importMeta };
} else if (typeof global !== 'undefined') {
  (global as any).import = { meta: importMeta };
} else if (typeof window !== 'undefined') {
  (window as any).import = { meta: importMeta };
}

export default importMeta;