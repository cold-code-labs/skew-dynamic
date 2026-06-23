import { defineConfig } from 'astro/config';

// Static site for skew-dynamic.coldcodelabs.com
export default defineConfig({
  site: 'https://skew-dynamic.coldcodelabs.com',
  output: 'static',
  build: { format: 'directory' },
  trailingSlash: 'ignore',
});
