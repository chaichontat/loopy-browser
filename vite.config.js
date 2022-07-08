import path from 'path';
import { searchForWorkspaceRoot } from 'vite';
import { sveltekit } from '@sveltejs/kit/vite';

/**
 * @type {import('vite').UserConfig}
 */
const config = {
  plugins: [sveltekit()],
  resolve: {
    alias: {
      $src: path.resolve('./src'),
      $comps: path.resolve('./src/lib/components')
    }
  },
  server: {
    fs: {
      allow: [searchForWorkspaceRoot(process.cwd())]
    }
  },
  build: {
    chunkSizeWarningLimit: 1024,
    rollupOptions: {
      output: {
        manualChunks: {
          'chart.js': ['chart.js'],
          // 'vega-embed': ['vega-embed'],
          'lru-cache': ['lru-cache'],
          ol: ['ol'],
          'tippy.js': ['tippy.js']
        }
      }
    }
  }
};
export default config;