export default {
 testEnvironment: 'jsdom',
 setupFilesAfterEnv: ['<rootDir>/src/setupTests.ts'],
 moduleNameMapper: {
   '^@/(.*)$': '<rootDir>/src/$1',
 },
 collectCoverage: true,
 collectCoverageFrom: [
   'src/**/*.{js,jsx,ts,tsx}',
   '!src/**/*.d.ts',
   '!src/main.tsx',
   '!src/vite-env.d.ts',
 ],
 coverageDirectory: 'coverage',
 coverageReporters: [
   'text',
   'lcov',
   'html'
 ],
 transform: {
   '^.+\\.(ts|tsx)$': 'ts-jest',
 },
 extensionsToTreatAsEsm: ['.ts', '.tsx'],
 globals: {
   'ts-jest': {
     useESM: true
   }
 }
};
