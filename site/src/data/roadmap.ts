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
  { n: 5, status: 'doing', pt: 'Corrida completa', en: 'Complete race',
    pt_d: 'Demo estável com física do terreno corrigida e tempo real; falta validar IA, corrida manual completa, HUD e áudio.', en_d: 'Stable demo with terrain physics fixed and real-time pacing; AI, a full manual race, HUD, and audio remain.' },
  { n: 6, status: 'todo', pt: 'Paridade e estabilidade', en: 'Parity and stability',
    pt_d: 'Menus, modos, saves e conteúdo original validados de ponta a ponta.', en_d: 'Menus, modes, saves, and original content validated end to end.' },
  { n: 7, status: 'todo', pt: 'Pacotes por plataforma', en: 'Platform packages',
    pt_d: 'Aplicativo macOS e builds Windows/Linux usando a cópia legal do usuário.', en_d: 'macOS app and Windows/Linux builds using the user’s legal copy.' },
  { n: 8, status: 'todo', pt: 'Melhorias e mods', en: 'Enhancements and mods',
    pt_d: 'Resolução, gráficos e SDK de mods somente depois da base original jogável.', en_d: 'Resolution, graphics, and mod SDK only after the original game is playable.' },
];
