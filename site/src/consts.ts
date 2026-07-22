export const SITE = {
  title: 'NASCAR Rumble ModSDK',
  tagline_pt: 'Engenharia reversa & SDK de modding open source',
  tagline_en: 'Reverse engineering & open-source modding SDK',
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

/** Estatísticas exibidas no hero — atualizar quando avançarmos. */
export const STATS = [
  { value: '2008', label_pt: 'funções mapeadas', label_en: 'functions mapped' },
  { value: '5', label_pt: 'formatos decodificados', label_en: 'formats decoded' },
  { value: '168', label_pt: 'carros catalogados', label_en: 'cars catalogued' },
  { value: '188k', label_pt: 'linhas de C# nativo', label_en: 'lines of native C#' },
];
