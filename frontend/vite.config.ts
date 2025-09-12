/// <reference types="vitest" />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    allowedHosts: ['localhost', '127.0.0.1', '192.168.1.137', 'admin.mestocker.com', 'mestocker.com'],
    proxy: {
      "/api": {
        target: "http://192.168.1.137:8000",
        changeOrigin: true,
        secure: false
      }
    }
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // Core React libraries
          vendor: ['react', 'react-dom'],
          // Router
          router: ['react-router-dom'],
          // UI components and icons
          ui: ['lucide-react'],
          // Charts library
          charts: ['recharts'],
          // Form libraries
          forms: ['react-hook-form'],
          // HTTP client
          http: ['axios'],
          // Utilities
          utils: ['date-fns', 'clsx']
        }
      }
    },
    chunkSizeWarningLimit: 1000,
    minify: 'esbuild', // Use esbuild for faster builds
    target: 'esnext',
    sourcemap: false, // Disable sourcemaps in production for smaller bundle
    cssCodeSplit: true, // Split CSS into separate files
    assetsInlineLimit: 4096, // Inline assets smaller than 4kb
    reportCompressedSize: true
  },
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react-router-dom',
      'lucide-react',
      'recharts',
      'react-hook-form'
    ]
  },
  define: {
    'process.env': {
      NODE_ENV: JSON.stringify(process.env.NODE_ENV || 'development'),
    },
    'process.env.NODE_ENV': JSON.stringify(
      process.env.NODE_ENV || 'development'
    ),
    global: 'globalThis',
    process: 'globalThis.process',
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    include: ['src/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}'],
    exclude: ['node_modules', 'dist', '.idea', '.git', '.cache'],
    coverage: {
      reporter: ['text', 'json', 'html'],
      include: ['src/**/*'],
      exclude: [
        'src/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}',
        'src/test/**/*',
      ],
    },
  },
});