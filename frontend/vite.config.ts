/// <reference types="vitest" />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: [
        'favicon.ico',
        'apple-touch-icon.png',
        'masked-icon.svg',
        'pwa-192x192.png',
        'pwa-512x512.png',
        'offline.html'
      ],
      manifest: {
        name: 'MeStocker - Marketplace Inteligente Bucaramanga',
        short_name: 'MeStocker',
        description: 'Marketplace inteligente en Bucaramanga. Conecta vendedores y compradores con tecnología colombiana.',
        theme_color: '#3b82f6',
        background_color: '#ffffff',
        display: 'standalone',
        orientation: 'portrait-primary',
        scope: '/',
        start_url: '/?utm_source=pwa',
        lang: 'es-CO',
        dir: 'ltr',
        categories: ['business', 'productivity', 'shopping', 'marketplace'],
        prefer_related_applications: false,
        icons: [
          {
            src: 'pwa-64x64.png',
            sizes: '64x64',
            type: 'image/png'
          },
          {
            src: 'pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png',
            purpose: 'any'
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'any'
          },
          {
            src: 'pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png',
            purpose: 'maskable'
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'maskable'
          }
        ],
        screenshots: [
          {
            src: 'screenshot-mobile-1.png',
            sizes: '390x844',
            type: 'image/png',
            platform: 'mobile',
            label: 'Marketplace principal en móvil'
          },
          {
            src: 'screenshot-mobile-2.png',
            sizes: '390x844',
            type: 'image/png',
            platform: 'mobile',
            label: 'Carrito de compras móvil'
          }
        ],
        shortcuts: [
          {
            name: 'Marketplace',
            short_name: 'Productos',
            description: 'Explorar productos del marketplace',
            url: '/marketplace?utm_source=shortcut',
            icons: [{
              src: 'pwa-192x192.png',
              sizes: '192x192',
              type: 'image/png'
            }]
          },
          {
            name: 'Mi Carrito',
            short_name: 'Carrito',
            description: 'Ver carrito de compras',
            url: '/marketplace/cart?utm_source=shortcut',
            icons: [{
              src: 'pwa-192x192.png',
              sizes: '192x192',
              type: 'image/png'
            }]
          },
          {
            name: 'Panel Vendedor',
            short_name: 'Vender',
            description: 'Acceder al panel de vendedor',
            url: '/vendor/dashboard?utm_source=shortcut',
            icons: [{
              src: 'pwa-192x192.png',
              sizes: '192x192',
              type: 'image/png'
            }]
          },
          {
            name: 'Mis Pedidos',
            short_name: 'Pedidos',
            description: 'Ver historial de pedidos',
            url: '/orders?utm_source=shortcut',
            icons: [{
              src: 'pwa-192x192.png',
              sizes: '192x192',
              type: 'image/png'
            }]
          }
        ],
        related_applications: [
          {
            platform: 'webapp',
            url: 'https://mestocker.com/app'
          }
        ]
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,jpg,jpeg,webp,woff,woff2,ttf,eot}'],
        maximumFileSizeToCacheInBytes: 5000000, // 5MB max file size
        runtimeCaching: [
          {
            urlPattern: /^https?:\/\/.*\/api\//i,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'mestocker-api-cache',
              networkTimeoutSeconds: 3,
              expiration: {
                maxEntries: 150,
                maxAgeSeconds: 60 * 60 * 2 // 2 hours
              },
              cacheableResponse: {
                statuses: [0, 200, 302, 404]
              },
              backgroundSync: {
                name: 'api-queue',
                options: {
                  maxRetentionTime: 24 * 60 // 24 hours
                }
              }
            }
          },
          {
            urlPattern: /\/api\/v1\/(products|marketplace)/i,
            handler: 'StaleWhileRevalidate',
            options: {
              cacheName: 'mestocker-products-cache',
              expiration: {
                maxEntries: 300,
                maxAgeSeconds: 60 * 60 * 6 // 6 hours
              },
              cacheableResponse: {
                statuses: [200]
              }
            }
          },
          {
            urlPattern: /\.(png|jpg|jpeg|svg|gif|webp|avif)$/i,
            handler: 'CacheFirst',
            options: {
              cacheName: 'mestocker-images-cache',
              expiration: {
                maxEntries: 250,
                maxAgeSeconds: 60 * 60 * 24 * 7 // 7 days
              },
              cacheableResponse: {
                statuses: [200]
              }
            }
          },
          {
            urlPattern: /\.(js|css|woff|woff2|ttf)$/i,
            handler: 'StaleWhileRevalidate',
            options: {
              cacheName: 'mestocker-static-cache',
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 60 * 60 * 24 * 30 // 30 days
              }
            }
          },
          {
            urlPattern: /\/offline\.html$/,
            handler: 'CacheFirst',
            options: {
              cacheName: 'mestocker-offline-cache'
            }
          }
        ],
        skipWaiting: true,
        clientsClaim: true,
        cleanupOutdatedCaches: true,
        offlineGoogleAnalytics: true,
        sourcemap: false,
        mode: 'production'
      },
      devOptions: {
        enabled: false, // DESACTIVADO: Service Worker causaba caché agresivo en desarrollo
        type: 'module'
      }
    })
  ],
  server: {
    host: '0.0.0.0',
    port: 5173,
    allowedHosts: [
      'mestocker.local',
      'localhost',
      '127.0.0.1',
      '192.168.1.137',
      'admin.mestocker.com',
      'mestocker.com',
      'proprivilege-nonnautically-debl.ngrok-free.dev',
      '.ngrok-free.dev'
    ],
    // Proxy enabled for development - forwards API requests to backend
    proxy: {
      "/api": {
        target: "http://192.168.1.137:8000",
        changeOrigin: true,
        secure: false,
        // Proxy /api/* to backend (backend handles /api/v1 prefix)
      }
    }
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: (id) => {
          // Core React libraries
          if (id.includes('node_modules')) {
            if (id.includes('react') || id.includes('react-dom')) {
              return 'vendor-react';
            }
            if (id.includes('react-router')) {
              return 'vendor-router';
            }
            if (id.includes('lucide-react') || id.includes('@heroicons')) {
              return 'vendor-icons';
            }
            if (id.includes('recharts') || id.includes('konva') || id.includes('react-konva')) {
              return 'vendor-charts';
            }
            if (id.includes('react-hook-form') || id.includes('@hookform') || id.includes('yup')) {
              return 'vendor-forms';
            }
            if (id.includes('axios') || id.includes('zustand')) {
              return 'vendor-state';
            }
            if (id.includes('@dnd-kit')) {
              return 'vendor-dnd';
            }
            if (id.includes('framer-motion')) {
              return 'vendor-animation';
            }
            if (id.includes('leaflet') || id.includes('react-leaflet')) {
              return 'vendor-maps';
            }
            if (id.includes('xlsx') || id.includes('file-saver') || id.includes('@react-pdf')) {
              return 'vendor-files';
            }
            // Other vendor libs
            return 'vendor-misc';
          }

          // Split application code by feature
          if (id.includes('/pages/admin/')) {
            return 'pages-admin';
          }
          if (id.includes('/pages/vendor/')) {
            return 'pages-vendor';
          }
          if (id.includes('/pages/')) {
            return 'pages-core';
          }
          if (id.includes('/components/admin/')) {
            return 'components-admin';
          }
          if (id.includes('/components/vendor/')) {
            return 'components-vendor';
          }
          if (id.includes('/components/marketplace/')) {
            return 'components-marketplace';
          }
          if (id.includes('/components/')) {
            return 'components-core';
          }
          if (id.includes('/services/')) {
            return 'services';
          }
        }
      },
      treeshake: {
        moduleSideEffects: false,
        propertyReadSideEffects: false,
        tryCatchDeoptimization: false
      }
    },
    chunkSizeWarningLimit: 500, // Reduced to enforce 500KB limit
    minify: 'esbuild',
    target: 'es2022', // Modern target for better optimization
    sourcemap: false,
    cssCodeSplit: true,
    assetsInlineLimit: 4096,
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