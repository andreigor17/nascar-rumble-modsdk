export type Phase = { n: number; status: 'done' | 'doing' | 'todo'; pt: string; en: string; pt_d: string; en_d: string };

export const ROADMAP: Phase[] = [
  { n: 1, status: 'done', pt: 'Referência original', en: 'Original reference',
    pt_d: 'Disco, executável, formatos e funções mapeados sem distribuir o jogo.', en_d: 'Disc, executable, formats, and functions mapped without distributing the game.' },
  { n: 2, status: 'done', pt: 'Build reproduzível', en: 'Reproducible build',
    pt_d: 'O SLUS_010.68 é reconstruído byte a byte com a toolchain fixada.', en_d: 'SLUS_010.68 is rebuilt byte-for-byte with a pinned toolchain.' },
  { n: 3, status: 'done', pt: 'Base nativa macOS', en: 'macOS native foundation',
    pt_d: 'Executável ARM abre janela própria e inicializa os subsistemas do jogo.', en_d: 'The ARM executable opens its own window and initializes game subsystems.' },
  { n: 4, status: 'done', pt: 'Intro e menu', en: 'Intro and menu',
    pt_d: 'Intro completa com áudio, skip original, carregamento, menu principal e controle funcionando.', en_d: 'Full intro with audio, original skip, loading, main menu, and input working.' },
  { n: 5, status: 'done', pt: 'Corrida completa', en: 'Complete race',
    pt_d: 'Corrida do grid à bandeirada com física e IA conferidas contra o PS1; campeonato completo com pontos e desbloqueios; 30 ou 60 fps.', en_d: 'Grid-to-flag race with physics and AI checked against the PS1; full championship with points and unlocks; 30 or 60 fps.' },
  { n: 6, status: 'doing', pt: 'Paridade e estabilidade', en: 'Parity and stability',
    pt_d: 'Single Race, Championship, Showdown, Time Trial e Showcase validados. Faltam memory card, 2 jogadores e a aderência da arrancada a 60 fps.', en_d: 'Single Race, Championship, Showdown, Time Trial and Showcase validated. Memory card, 2 players and 60 fps launch grip remain.' },
  { n: 7, status: 'todo', pt: 'Pacotes por plataforma', en: 'Platform packages',
    pt_d: 'Aplicativo macOS e builds Windows/Linux usando a cópia legal do usuário.', en_d: 'macOS app and Windows/Linux builds using the user’s legal copy.' },
  { n: 8, status: 'todo', pt: 'Melhorias e mods', en: 'Enhancements and mods',
    pt_d: 'Resolução, gráficos e SDK de mods somente depois da base original jogável.', en_d: 'Resolution, graphics, and mod SDK only after the original game is playable.' },
];
