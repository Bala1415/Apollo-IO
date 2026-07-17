import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import webExtension from 'vite-plugin-web-extension'
import { resolve } from 'path'

export default defineConfig({
  plugins: [
    react(),
    webExtension({
      manifest: resolve(__dirname, 'manifest.json'),
      additionalInputs: [],
      disableAutoLaunch: true,
      webExtConfig: {
        startUrl: 'https://www.google.com',
      },
    }),
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@ai-browser-intelligence/shared-types': resolve(
        __dirname,
        '../../packages/shared-types/src/index.ts'
      ),
      '@ai-browser-intelligence/taxonomy': resolve(
        __dirname,
        '../../packages/taxonomy/src/index.ts'
      ),
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: process.env['NODE_ENV'] !== 'production',
    minify: process.env['NODE_ENV'] === 'production',
    rollupOptions: {
      output: {
        chunkFileNames: 'chunks/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]',
      },
    },
  },
})
