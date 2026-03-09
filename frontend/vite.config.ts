import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  // base path richiesto da GitHub Pages: https://<user>.github.io/<repo>/
  base: '/copytradingame/',
})
