import type { Config } from 'jest';

const config: Config = {
  // Directorios raíz para buscar tests
  roots: ['<rootDir>/src'],

  // Transformaciones de archivos
  transform: {
    '^.+\\.tsx?$': ['ts-jest', {
      tsconfig: {
        jsx: 'react-jsx',
      },
    }],
  },

  // Entorno de testing (jsdom para React)
  testEnvironment: 'jsdom',

  // Setup files que se ejecutan después del entorno
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.ts'],

  // Extensiones de archivos reconocidas
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node'],

  // Mapeo de módulos simplificado y corregido
  moduleNameMapper: {
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '\\.(gif|ttf|eot|png|jpg|jpeg|webp)$': '<rootDir>/src/__mocks__/fileMock.js',
    '\\.svg$': '<rootDir>/src/__mocks__/svgMock.js',
  },

  // Patrones de archivos de test
  testMatch: [
    '<rootDir>/src/**/__tests__/**/*.(ts|tsx|js)',
    '<rootDir>/src/**/?(*.)(test|spec).(ts|tsx|js)',
  ],

  // Cobertura de código
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/index.tsx',
    '!src/main.tsx',
    '!src/serviceWorker.ts',
  ],

  // Umbrales de cobertura
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 30,
      lines: 70,
      statements: 70,
    },
  },

  // Directorio de reportes de cobertura
  coverageDirectory: 'coverage',

  // Ignorar node_modules excepto algunos paquetes
  transformIgnorePatterns: [
    'node_modules/(?!(.*\\.mjs$|@testing-library))',
  ],
};

export default config;
