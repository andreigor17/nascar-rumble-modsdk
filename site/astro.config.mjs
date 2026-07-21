// @ts-check
import { defineConfig } from 'astro/config';

// Para deploy no GitHub Pages (repo "nascar-rumble-modsdk"), o site fica em
// https://<user>.github.io/nascar-rumble-modsdk/ — por isso o `base`.
// Em dev (`astro dev`) o base é aplicado igualmente; use o helper `href()` nos links.
export default defineConfig({
  site: 'https://andreigor17.github.io',
  base: '/nascar-rumble-modsdk',
  trailingSlash: 'ignore',
  build: { format: 'directory' },
});
