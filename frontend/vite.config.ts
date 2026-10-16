/*
 * Vite development/build configuration. React transforms JSX, Tailwind
 * provides generated utilities, and the local dev server requests port 3000.
 * API requests still use the base URL configured in src/services/api.ts.
 */

import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 3000,
    open: false,
  },
});
