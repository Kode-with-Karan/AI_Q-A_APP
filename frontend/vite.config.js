import { defineConfig } from 'vite'

// Proxy /api requests to backend running on localhost:8000 in development
export default defineConfig({
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
})
