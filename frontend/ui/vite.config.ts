import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // Add this 'server' block
  server: {
    port: 3000, // This is the port your React app will run on
    proxy: {
      // Proxy requests from /api to the Django backend
      '/api': {
        target: 'http://127.0.0.1:8000', // Your Django backend URL
        changeOrigin: true,
        secure: false,
      },
      // Proxy media files (e.g., file uploads)
      '/media': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
      }
    }
  }
})