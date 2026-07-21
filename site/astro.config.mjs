// @ts-check
import { defineConfig } from 'astro/config';

// Domínio personalizado: o site é servido na RAIZ de rumble.irontech.dev.br,
// por isso base = '/'. (O arquivo public/CNAME define o domínio no GitHub Pages.)
export default defineConfig({
  site: 'https://rumble.irontech.dev.br',
  base: '/',
  trailingSlash: 'ignore',
  build: { format: 'directory' },
});
