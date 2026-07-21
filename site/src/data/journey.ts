export type Step = { key: string; status: 'done' | 'doing' | 'todo'; pt: string; en: string };

/** Marcos rumo a "qualquer pessoa poder acessar/jogar/modar" — estilo status do online-ctr. */
export const JOURNEY: Step[] = [
  { key: 'understand', status: 'doing', pt: 'Entender o jogo', en: 'Understand the game' },
  { key: 'extract', status: 'doing', pt: 'Extrair os recursos', en: 'Extract the assets' },
  { key: 'tools', status: 'todo', pt: 'Editores & mods', en: 'Editors & mods' },
  { key: 'playable', status: 'todo', pt: 'Rodar sem emulador', en: 'Run without emulator' },
];

export const JOURNEY_STATUS = {
  pt: 'Em pesquisa — ainda não jogável. Acompanhe cada passo até lá.',
  en: 'In research — not playable yet. Follow every step toward that.',
};
