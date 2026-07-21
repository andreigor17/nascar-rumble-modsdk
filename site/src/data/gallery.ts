export type Shot = { src: string; pt: string; en: string };

export const GALLERY: Shot[] = [
  { src: '/gallery/help1-loading.png',
    pt: 'Tela "LOADING" (HELP1.LSC) decodificada de MDEC para PNG — 320×256.',
    en: '"LOADING" screen (HELP1.LSC) decoded from MDEC to PNG — 320×256.' },
  { src: '/gallery/texture-atlas.png',
    pt: 'Atlas de textura de uma pista, em cores: logo "NASCAR RUMBLE", pneus, grama e asfalto. Decodificado por região.',
    en: 'Track texture atlas, in color: "NASCAR RUMBLE" logo, tires, grass and asphalt. Decoded per region.' },
  { src: '/gallery/car-livery.png',
    pt: 'Pintura de um carro extraída do GlblData — o #43 do Richard Petty. São 171 liveries no jogo.',
    en: 'A car livery extracted from GlblData — Richard Petty’s #43. The game has 171 liveries.' },
  { src: '/gallery/track-jt3.png',
    pt: 'Traçado da pista JT3 a partir da linha central (Ctrk/TCRV) — um oval de NASCAR.',
    en: 'JT3 track layout from the centerline (Ctrk/TCRV) — a NASCAR oval.' },
];
