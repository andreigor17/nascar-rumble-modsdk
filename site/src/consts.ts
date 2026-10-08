import progress from '../../progress.json';

export const SITE = {
  title: 'NASCAR Rumble Native',
  url: 'https://rumble.irontech.dev.br',
  tagline_pt: 'NASCAR Rumble (PS1) rodando nativo, sem emulador: corrida completa e campeonato inteiro. Projeto de fã, open source.',
  tagline_en: 'NASCAR Rumble (PS1) running natively, no emulator: complete races and a whole championship. Open-source fan project.',
  github: 'https://github.com/andreigor17/nascar-rumble-modsdk',
  reference: 'https://www.online-ctr.com/',
};

export type Lang = 'pt' | 'en';

/** Prefixa BASE_URL para links internos funcionarem no GitHub Pages e em dev. */
export function href(path: string, lang: Lang = 'pt'): string {
  const base = import.meta.env.BASE_URL.replace(/\/$/, '');
  const prefix = lang === 'en' ? '/en' : '';
  const clean = path === '/' ? '' : path;
  return `${base}${prefix}${clean}` || '/';
}

/** Números da vitrine (estilo contadores do online-ctr). */
export const STATS = [
  { value: `${progress.functions.total}`, label_pt: 'funções do jogo rodando como código nativo', label_en: 'game functions running as native code' },
  { value: '3/3', label_pt: 'etapas de campeonato completas', label_en: 'championship rounds completed' },
  { value: '60', label_pt: 'fps opcionais na corrida', label_en: 'optional race fps' },
  { value: '171', label_pt: 'pinturas reais da NASCAR no disco', label_en: 'real NASCAR liveries on the disc' },
];

/** Decompilação byte a byte (matching), mostrada no roadmap. */
export const MATCHING = {
  code: `${progress.code.percent.toFixed(3)}%`,
  functions: `${progress.functions.matched}/${progress.functions.total}`,
};
