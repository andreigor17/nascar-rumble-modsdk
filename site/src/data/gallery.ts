export type Shot = { src: string; pt: string; en: string };

export const GALLERY: Shot[] = [
  { src: '/gallery/help1-loading.png',
    pt: 'Tela "LOADING" (HELP1.LSC) decodificada de MDEC para PNG — 320×256.',
    en: '"LOADING" screen (HELP1.LSC) decoded from MDEC to PNG — 320×256.' },
  { src: '/gallery/texture-atlas.png',
    pt: 'Atlas de textura (Cpag) de uma pista: logo EA, "LEGEND", rodas. Pixels 4bpp (cores a refinar).',
    en: 'Track texture atlas (Cpag): EA logo, "LEGEND", wheels. 4bpp pixels (colors to be refined).' },
  { src: '/gallery/track-jt3.png',
    pt: 'Traçado da pista JT3 a partir da linha central (Ctrk/TCRV) — um oval de NASCAR.',
    en: 'JT3 track layout from the centerline (Ctrk/TCRV) — a NASCAR oval.' },
];
