/**
 * Enterprise Production Build Configuration
 *
 * Optimized Vite configuration for production deployment with enterprise-grade
 * performance optimizations, advanced code splitting, and bundle analysis.
 *
 * Features:
 * - Advanced code splitting strategy
 * - Tree shaking optimization
 * - Compression and minification
 * - Bundle size optimization
 * - Performance monitoring
 * - Source map optimization
 * - Asset optimization
 * - PWA optimization
 *
 * @version 1.0.0
 * @author Frontend Performance AI
 */

/// <reference types="vitest" />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';
import { visualizer } from 'rollup-plugin-visualizer';
import { compression } from 'vite-plugin-compression';
import { ManifestOptions } from 'vite-plugin-pwa';

// Performance budgets (in KB)
const PERFORMANCE_BUDGETS = {
  MAIN_BUNDLE: 2048,      // 2MB main bundle
  VENDOR_BUNDLE: 1024,    // 1MB vendor bundle
  CHUNK_SIZE: 512,        // 512KB per chunk
  CSS_SIZE: 256,          // 256KB CSS
  ASSET_SIZE: 512         // 512KB assets
};

// Enhanced PWA manifest
const pwaManifest: Partial<ManifestOptions> = {
  name: 'MeStocker - Enterprise Admin Portal',
  short_name: 'MeStocker Admin',
  description: 'Advanced inventory management and marketplace administration',
  theme_color: '#3b82f6',
  background_color: '#ffffff',
  display: 'standalone',
  orientation: 'portrait-primary',
  scope: '/admin/',
  start_url: '/admin/dashboard?utm_source=pwa',
  lang: 'es-CO',
  dir: 'ltr',
  categories: ['business', 'productivity', 'administration'],
  prefer_related_applications: false,
  edge_side_includes: false,
  icons: [
    {
      src: 'admin-icon-192.png',
      sizes: '192x192',
      type: 'image/png',
      purpose: 'any maskable'
    },
    {
      src: 'admin-icon-512.png',
      sizes: '512x512',
      type: 'image/png',
      purpose: 'any maskable'
    }
  ]
};

export default defineConfig({
  plugins: [
    react({
      // React optimization for production
      jsxImportSource: '@emotion/react',
      babel: {
        plugins: [
          // Remove development helpers
          ['babel-plugin-transform-remove-console', { exclude: ['error', 'warn'] }],
          // Optimize imports
          ['babel-plugin-import', {
            libraryName: 'lodash',
            libraryDirectory: '',
            camel2DashComponentName: false
          }, 'lodash'],
          ['babel-plugin-import', {
            libraryName: 'react-icons',
            libraryDirectory: '',
            camel2DashComponentName: false
          }, 'react-icons']
        ]
      }
    }),

    // Enhanced PWA configuration
    VitePWA({
      registerType: 'autoUpdate',
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,jpg,jpeg,webp,woff,woff2,ttf,eot}'],
        maximumFileSizeToCacheInBytes: 3000000, // 3MB
        runtimeCaching: [
          // API Cache Strategy
          {
            urlPattern: /^https?:\/\/.*\/api\/v1\//i,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'admin-api-cache',
              networkTimeoutSeconds: 5,
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 60 * 60 * 1 // 1 hour
              },
              cacheableResponse: {
                statuses: [0, 200]
              }
            }
          },
          // Static Assets Cache
          {
            urlPattern: /\.(js|css|woff|woff2|ttf)$/i,
            handler: 'StaleWhileRevalidate',
            options: {
              cacheName: 'admin-static-cache',
              expiration: {
                maxEntries: 50,
                maxAgeSeconds: 60 * 60 * 24 * 7 // 7 days
              }
            }
          },
          // Image Cache
          {
            urlPattern: /\.(png|jpg|jpeg|svg|gif|webp|avif)$/i,
            handler: 'CacheFirst',
            options: {
              cacheName: 'admin-images-cache',
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 60 * 60 * 24 * 30 // 30 days
              }
            }
          }
        ],
        cleanupOutdatedCaches: true,
        skipWaiting: true,
        clientsClaim: true
      },
      manifest: pwaManifest,
      devOptions: {
        enabled: false // Disable in development
      }
    }),

    // Bundle analyzer
    visualizer({
      filename: 'dist/bundle-analysis.html',
      open: false,
      gzipSize: true,
      brotliSize: true,
      template: 'treemap' // 'treemap', 'sunburst', 'network'
    }),

    // Compression plugins
    compression({
      algorithm: 'gzip',
      threshold: 1024, // Only compress files larger than 1KB
      deleteOriginFile: false
    }),
    compression({
      algorithm: 'brotliCompress',
      ext: '.br',
      threshold: 1024,
      deleteOriginFile: false
    })
  ],

  // Build configuration
  build: {
    target: 'es2022',
    minify: 'esbuild',
    sourcemap: false, // Disable source maps for production
    cssCodeSplit: true,
    assetsInlineLimit: 4096, // 4KB
    reportCompressedSize: true,
    chunkSizeWarningLimit: PERFORMANCE_BUDGETS.CHUNK_SIZE,

    rollupOptions: {
      // External dependencies (if using CDN)
      external: [],

      output: {
        // Advanced code splitting strategy
        manualChunks: (id) => {
          // Node modules splitting
          if (id.includes('node_modules')) {
            // React core
            if (id.includes('react') || id.includes('react-dom')) {
              return 'vendor-react';
            }

            // Router
            if (id.includes('react-router')) {
              return 'vendor-router';
            }

            // Icons (separate chunks for tree shaking)
            if (id.includes('lucide-react')) {
              return 'vendor-icons-lucide';
            }
            if (id.includes('@heroicons/react')) {
              return 'vendor-icons-heroicons';
            }
            if (id.includes('react-icons')) {
              return 'vendor-icons-react';
            }

            // Charts and visualization
            if (id.includes('recharts')) {
              return 'vendor-charts-recharts';
            }
            if (id.includes('konva') || id.includes('react-konva')) {
              return 'vendor-charts-konva';
            }

            // Forms
            if (id.includes('react-hook-form') || id.includes('@hookform') || id.includes('yup')) {
              return 'vendor-forms';
            }

            // State management
            if (id.includes('zustand')) {
              return 'vendor-state';
            }

            // HTTP and async
            if (id.includes('axios')) {
              return 'vendor-http';
            }

            // UI Libraries
            if (id.includes('framer-motion')) {
              return 'vendor-animation';
            }
            if (id.includes('@dnd-kit')) {
              return 'vendor-dnd';
            }

            // Maps
            if (id.includes('leaflet') || id.includes('react-leaflet')) {
              return 'vendor-maps';
            }

            // File handling
            if (id.includes('xlsx') || id.includes('file-saver') || id.includes('@react-pdf')) {
              return 'vendor-files';
            }

            // Utility libraries
            if (id.includes('lodash') || id.includes('date-fns')) {
              return 'vendor-utils';
            }

            // Everything else
            return 'vendor-misc';
          }

          // Application code splitting by feature
          if (id.includes('src/')) {
            // Admin navigation system
            if (id.includes('/navigation/')) {
              return 'admin-navigation';
            }

            // Admin pages by category
            if (id.includes('/admin/') && id.includes('Dashboard')) {
              return 'admin-dashboards';
            }
            if (id.includes('/admin/') && (id.includes('User') || id.includes('user'))) {
              return 'admin-users';
            }
            if (id.includes('/admin/') && (id.includes('Vendor') || id.includes('vendor'))) {
              return 'admin-vendors';
            }
            if (id.includes('/admin/') && (id.includes('Inventory') || id.includes('Product'))) {
              return 'admin-inventory';
            }
            if (id.includes('/admin/') && (id.includes('Warehouse') || id.includes('Location'))) {
              return 'admin-warehouse';
            }
            if (id.includes('/admin/') && (id.includes('Report') || id.includes('Analytics'))) {
              return 'admin-reports';
            }

            // Core components
            if (id.includes('/components/common/')) {
              return 'components-common';
            }
            if (id.includes('/components/admin/')) {
              return 'components-admin';
            }

            // Services and utilities
            if (id.includes('/services/')) {
              return 'services';
            }
            if (id.includes('/utils/')) {
              return 'utils';
            }
            if (id.includes('/hooks/')) {
              return 'hooks';
            }

            // Stores
            if (id.includes('/stores/')) {
              return 'stores';
            }
          }

          // Default chunk
          return 'main';
        },

        // Optimize chunk names
        chunkFileNames: (chunkInfo) => {
          const { name } = chunkInfo;

          // Performance-optimized file naming
          if (name.startsWith('vendor-')) {
            return `assets/vendors/[name]-[hash].js`;
          }
          if (name.startsWith('admin-')) {
            return `assets/admin/[name]-[hash].js`;
          }
          if (name.startsWith('components-')) {
            return `assets/components/[name]-[hash].js`;
          }

          return `assets/chunks/[name]-[hash].js`;
        },

        // Optimize asset names
        assetFileNames: (assetInfo) => {
          const { name } = assetInfo;

          // CSS files
          if (name?.endsWith('.css')) {
            return 'assets/styles/[name]-[hash].css';
          }

          // Fonts
          if (/\.(woff|woff2|ttf|eot)$/.test(name || '')) {
            return 'assets/fonts/[name]-[hash][extname]';
          }

          // Images
          if (/\.(png|jpg|jpeg|svg|gif|webp|avif)$/.test(name || '')) {
            return 'assets/images/[name]-[hash][extname]';
          }

          return 'assets/[name]-[hash][extname]';
        }
      },

      // Tree shaking configuration
      treeshake: {
        moduleSideEffects: false,
        propertyReadSideEffects: false,
        tryCatchDeoptimization: false,
        unknownGlobalSideEffects: false
      }
    },

    // CSS optimization
    cssMinify: 'esbuild',

    // Enable polyfills for older browsers if needed
    polyfillModulePreload: true
  },

  // Optimization dependencies
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react-router-dom',
      'zustand',
      'axios'
    ],
    exclude: [
      // Exclude large libraries to be loaded separately
      'recharts',
      'konva',
      'react-konva',
      'leaflet',
      'react-leaflet'
    ]
  },

  // Performance monitoring
  define: {
    __PERFORMANCE_MONITORING__: JSON.stringify(true),
    __BUNDLE_ANALYSIS__: JSON.stringify(true),
    'process.env.NODE_ENV': JSON.stringify('production'),
    'process.env.VITE_PERFORMANCE_BUDGET_MAIN': JSON.stringify(PERFORMANCE_BUDGETS.MAIN_BUNDLE),
    'process.env.VITE_PERFORMANCE_BUDGET_VENDOR': JSON.stringify(PERFORMANCE_BUDGETS.VENDOR_BUNDLE),
    'process.env.VITE_PERFORMANCE_BUDGET_CHUNK': JSON.stringify(PERFORMANCE_BUDGETS.CHUNK_SIZE)
  },

  // Server configuration for production preview
  preview: {
    port: 4173,
    host: true,
    strictPort: true,
    open: false
  },

  // ESBuild configuration
  esbuild: {
    drop: ['console', 'debugger'], // Remove console logs and debugger statements
    legalComments: 'none',
    minifyIdentifiers: true,
    minifySyntax: true,
    minifyWhitespace: true,
    treeShaking: true
  }
});