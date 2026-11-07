import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Local Windows/macOS/Linux development runs Django on localhost.
// Docker Compose overrides API_PROXY_TARGET with http://api:8000.
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: process.env.API_PROXY_TARGET || 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
});
