import progress from '../../progress.json';

export const SITE = {
  title: 'NASCAR Rumble ModSDK',
  tagline_pt: 'Port nativo & engenharia reversa open source',
  tagline_en: 'Native port & open-source reverse engineering',
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

/** Métricas matching vêm do manifesto canônico gerado na raiz do repositório. */
export const STATS = [
  { value: `${progress.code.percent.toFixed(3)}%`, label_pt: 'código matching', label_en: 'matching code' },
  {
    value: `${progress.functions.matched}/${progress.functions.total}`,
    label_pt: 'funções matching',
    label_en: 'matching functions',
  },
  { value: '5', label_pt: 'formatos decodificados', label_en: 'formats decoded' },
  { value: '168', label_pt: 'carros catalogados', label_en: 'cars catalogued' },
];
