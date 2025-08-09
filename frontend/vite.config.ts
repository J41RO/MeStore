import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Permitir conexiones desde cualquier IP
    port: 5173,
    strictPort: true,
  },
});
