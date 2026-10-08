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
  pt: 'Primeiro quadro confirmado: o port nativo já mostra o logo da EA. Agora estamos estabilizando áudio e intro até chegar ao menu.',
  en: 'First frame confirmed: the native port now shows the EA logo. We are stabilizing audio and intro playback on the way to the menu.',
};
