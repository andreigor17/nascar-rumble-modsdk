export type Step = { key: string; status: 'done' | 'doing' | 'todo'; pt: string; en: string };

/** Marcos rumo a "qualquer pessoa poder acessar/jogar/modar" — estilo status do online-ctr. */
export const JOURNEY: Step[] = [
  { key: 'understand', status: 'doing', pt: 'Entender o jogo', en: 'Understand the game' },
  { key: 'native', status: 'done', pt: 'Criar a base nativa', en: 'Build the native foundation' },
  { key: 'boot', status: 'done', pt: 'Exibir intro e menu', en: 'Show intro and menu' },
  { key: 'race', status: 'doing', pt: 'Completar uma corrida', en: 'Complete a race' },
  { key: 'package', status: 'todo', pt: 'Empacotar para Mac/Windows/Linux', en: 'Package for Mac/Windows/Linux' },
  { key: 'mods', status: 'todo', pt: 'Melhorias e mods', en: 'Enhancements and mods' },
];

export const JOURNEY_STATUS = {
  pt: 'Intro, menu e demo de corrida estáveis no port nativo, com os carros no chão. Agora estamos validando a IA e uma corrida completa.',
  en: 'Intro, menu, and the race demo are stable in the native port, with cars on the ground. We are now validating the AI and a complete race.',
};
