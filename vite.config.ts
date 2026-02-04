import path from 'path';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  // 1. CRITICAL FIX: Base Path
  // This ensures assets are loaded via relative paths ("./assets/...") 
  // preventing 404 errors when deployed on OpenShift/Nginx.
  base: './',

  plugins: [react()],

  // 2. Server Settings (For local development only)
  server: {
    port: 3000,
    host: '0.0.0.0',
  },

  // 3. Resolve Alias (Preserved from your original file)
  // This allows imports like "import X from '@/components/X'"
  resolve: {
    alias: {
      '@': path.resolve(__dirname, '.'),
    },
  },
});
