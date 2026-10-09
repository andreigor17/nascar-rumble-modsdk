export type Step = {
  key: string;
  status: 'done' | 'doing' | 'todo';
  pt: string;
  en: string;
  /** "Total" column of the results-style milestone panel: the date it was reached. */
  date?: string;
};

/** Milestones toward "anyone can play/mod it", shown as the game's race results screen. */
export const JOURNEY: Step[] = [
  { key: 'understand', status: 'done', date: '2026-07-21', pt: 'Disco, formatos e executável mapeados', en: 'Disc, formats and executable mapped' },
  { key: 'native', status: 'done', date: '2026-10-07', pt: 'Primeiro quadro nativo (logo da EA)', en: 'First native frame (EA logo)' },
  { key: 'boot', status: 'done', date: '2026-10-08', pt: 'Intro, menu e controle', en: 'Intro, menu and controls' },
  { key: 'race', status: 'done', date: '2026-10-08', pt: 'Corrida completa com IA e física corretas', en: 'Complete race with correct AI and physics' },
  { key: 'modes', status: 'done', date: '2026-10-08', pt: 'Campeonato completo, Showdown e Time Trial', en: 'Full championship, Showdown and Time Trial' },
  { key: 'memcard', status: 'done', date: '2026-10-08', pt: 'Salvar e carregar no memory card', en: 'Saving and loading on the memory card' },
  { key: 'parity', status: 'doing', pt: '2 jogadores e paridade fina', en: '2 players and fine parity' },
  { key: 'package', status: 'todo', pt: 'Pacotes para Mac, Windows e Linux', en: 'Packages for Mac, Windows and Linux' },
  { key: 'mods', status: 'todo', pt: 'Widescreen, alta resolução e mods', en: 'Widescreen, high resolution and mods' },
];

export const JOURNEY_STATUS = {
  pt: 'Do boot à bandeirada: o port nativo roda uma corrida completa e um campeonato inteiro, com pontos e desbloqueios, e agora salva o progresso no memory card. Próximo: 2 jogadores.',
  en: 'From boot to the checkered flag: the native port runs a complete race and a whole championship, with points and unlocks, and now saves progress to the memory card. Next: 2 players.',
};
