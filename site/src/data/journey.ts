export type Step = { key: string; status: 'done' | 'doing' | 'todo'; pt: string; en: string };

/** Marcos rumo a "qualquer pessoa poder acessar/jogar/modar" — estilo status do online-ctr. */
export const JOURNEY: Step[] = [
  { key: 'understand', status: 'doing', pt: 'Entender o jogo', en: 'Understand the game' },
  { key: 'native', status: 'done', pt: 'Criar a base nativa', en: 'Build the native foundation' },
  { key: 'boot', status: 'doing', pt: 'Exibir intro e menu', en: 'Show intro and menu' },
  { key: 'race', status: 'todo', pt: 'Completar uma corrida', en: 'Complete a race' },
  { key: 'package', status: 'todo', pt: 'Empacotar para Mac/Windows/Linux', en: 'Package for Mac/Windows/Linux' },
  { key: 'mods', status: 'todo', pt: 'Melhorias e mods', en: 'Enhancements and mods' },
];

export const JOURNEY_STATUS = {
  pt: 'O executável macOS ARM abre a janela e inicia o jogo original; estamos corrigindo a leitura de CD antes do primeiro quadro.',
  en: 'The macOS ARM executable opens a window and starts the original game; we are fixing CD reads before the first frame.',
};
