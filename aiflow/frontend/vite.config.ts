import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],

  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components'),
      '@stores': path.resolve(__dirname, './src/stores'),
      '@utils': path.resolve(__dirname, './src/utils'),
      '@types': path.resolve(__dirname, './src/types'),
    },
  },

  server: {
    port: 5173,
    open: true,
    // CORS配置：开发环境宽松，生产环境严格
    cors: {
      origin: process.env.VITE_CORS_ORIGIN?.split(',') || true,
      credentials: true,
      methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
      allowedHeaders: ['Content-Type', 'Authorization'],
    },
    // 代理配置示例（如需访问外部API）
    // proxy: {
    //   '/api': {
    //     target: 'http://localhost:8000',
    //     changeOrigin: true,
    //     rewrite: (path) => path.replace(/^\/api/, '')
    //   }
    // },
  },

  build: {
    outDir: 'dist',
    sourcemap: true,
    // Chunk splitting for optimal loading
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'visualization': ['cytoscape', 'cytoscape-dagre', 'd3'],
          'editor': ['monaco-editor', '@monaco-editor/react'],
          'state': ['zustand'],
        },
      },
    },
    // Performance optimizations
    chunkSizeWarningLimit: 1000,
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
      },
    },
  },

  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'zustand',
      'cytoscape',
      'cytoscape-dagre',
      'd3',
      'monaco-editor',
      '@monaco-editor/react',
      'pako',
    ],
  },

  // CSS preprocessing
  css: {
    modules: {
      localsConvention: 'camelCase',
    },
    preprocessorOptions: {
      scss: {
        additionalData: `@import "@/styles/variables.scss";`,
      },
    },
  },
})
