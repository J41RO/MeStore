module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.ts'],
  setupFiles: ['<rootDir>/src/jest.setup.js'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '^./TestComponent$': '<rootDir>/src/__mocks__/TestComponent.tsx',
    '^../TestComponent$': '<rootDir>/src/__mocks__/TestComponent.tsx',
    '^../services/api$': '<rootDir>/src/__mocks__/api.ts',
    '^../../services/api$': '<rootDir>/src/__mocks__/api.ts',
    '^../services/PaymentService$': '<rootDir>/src/__mocks__/PaymentService.ts',
    '^../../services/PaymentService$': '<rootDir>/src/__mocks__/PaymentService.ts',
    '^../services/CartService$': '<rootDir>/src/__mocks__/CartService.ts',
    '^../../services/CartService$': '<rootDir>/src/__mocks__/CartService.ts',
    '^../services/websocketService$': '<rootDir>/src/__mocks__/websocketService.ts',
    '^../../services/websocketService$': '<rootDir>/src/__mocks__/websocketService.ts',
    '^../stores/analyticsStore$': '<rootDir>/src/__mocks__/analyticsStore.ts',
    '^../../stores/analyticsStore$': '<rootDir>/src/__mocks__/analyticsStore.ts',
    'react-beautiful-dnd': '<rootDir>/src/__mocks__/react-beautiful-dnd.ts',
    'jest-websocket-mock': '<rootDir>/src/__mocks__/jest-websocket-mock.ts',
  },
  globals: {
    'import.meta': {
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
    },
    'ts-jest': {
      isolatedModules: true,
      useESM: false,
    },
  },
  transform: {
    '^.+\\.(ts|tsx)$': ['babel-jest', {
      presets: [
        ['@babel/preset-env', { targets: { node: 'current' } }],
        ['@babel/preset-react', { runtime: 'automatic' }],
        '@babel/preset-typescript',
      ],
      plugins: [
        [
          'babel-plugin-transform-import-meta',
          {
            module: 'ES6',
            getUrl: () => 'file://localhost/test',
            getEnv: () => ({
              VITE_API_BASE_URL: 'http://localhost:8000',
              VITE_BUILD_NUMBER: '1',
              MODE: 'test',
              DEV: false,
              PROD: false,
              BASE_URL: '/',
            }),
          },
        ],
      ],
    }],
    '^.+\\.(js|jsx)$': ['babel-jest', {
      presets: [
        ['@babel/preset-env', { targets: { node: 'current' } }],
        ['@babel/preset-react', { runtime: 'automatic' }],
      ],
      plugins: [
        [
          'babel-plugin-transform-import-meta',
          {
            module: 'ES6',
            getUrl: () => 'file://localhost/test',
            getEnv: () => ({
              VITE_API_BASE_URL: 'http://localhost:8000',
              VITE_BUILD_NUMBER: '1',
              MODE: 'test',
              DEV: false,
              PROD: false,
              BASE_URL: '/',
            }),
          },
        ],
      ],
    }],
  },
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node'],
  testMatch: [
    '<rootDir>/src/**/__tests__/**/*.(ts|tsx|js)',
    '<rootDir>/src/**/?(*.)(spec|test).(ts|tsx|js)',
  ],
  collectCoverageFrom: [
    'src/**/*.(ts|tsx)',
    '!src/**/*.d.ts',
    '!src/index.tsx',
    '!src/setupTests.ts',
    '!src/jest.setup.js',
  ],
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'html'],
  transformIgnorePatterns: [
    'node_modules/(?!(@testing-library|@react-router|react-router|lodash-es)/)',
  ],
  testEnvironmentOptions: {
    customExportConditions: ['node', 'node-addons'],
  },
};
