import path from 'path';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  base: './', // Critical for OpenShift
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, '.'),
    },
  },
  // --- ADD THIS BLOCK ---
  define: {
    // This creates a fake "process.env" object in the browser
    // so your code doesn't crash when it tries to read from it.
    'process.env': {},
  },
});
