import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: true,   // Permite acceso desde Docker
    port: 8080,   // Puerto del frontend
    strictPort: true,
    proxy: {
      "/api": {
        target: "http://backend:5000", // Nombre del servicio en docker-compose
        changeOrigin: true,
        secure: false,
      }
    }
  }
});
