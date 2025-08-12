import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  root: './',
  build: {
    outDir: '../src/static', // Saída para a pasta static do Flask
    emptyOutDir: true, // Limpa a pasta de saída antes de construir
  },
  server: {
    proxy: {
      '/api': 'http://localhost:5000', // Proxy para o backend Flask
    },
  },
})

