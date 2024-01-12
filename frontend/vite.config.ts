import { defineConfig } from 'vite';
import postcssNesting from 'postcss-nesting';
import react from '@vitejs/plugin-react';

export default defineConfig({
  base: './',
  plugins: [react()],
  resolve: {
    alias: {
      '~': '/src',
    },
  },
  css: {
    postcss: {
      plugins: [postcssNesting],
    },
  },
  server: {
    port: 8080,
  },
});
