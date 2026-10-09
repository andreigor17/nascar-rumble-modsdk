/**
 * What runs in the native port today, mode by mode — checked in the macOS ARM build by driving
 * the real menus (notes/SESSION_011.md and devlog 016). Status words follow the game's own
 * results screen: "Finished" (green), "Racing..." (in progress) and "DNF" (blocked).
 */
export type ModeStatus = 'finished' | 'racing' | 'dnf';

export type Mode = {
  name: string; // the game's own menu label
  status: ModeStatus;
  pt: string;
  en: string;
};

export const MODES: Mode[] = [
  { name: 'Single Race', status: 'finished',
    pt: 'Escolha de carro, pista e oponentes; corrida completa até os resultados e de volta ao menu.',
    en: 'Car, track and opponent selection; a complete race through the results and back to the menu.' },
  { name: 'Championship', status: 'finished',
    pt: 'Copa Gold Rush inteira: 3 etapas, nome do piloto, pontos, classificação geral e desbloqueios (classe Pro, Bad Lands, Mardi Gras, pistas bônus).',
    en: 'The whole Gold Rush cup: 3 rounds, driver name, points, overall standings and unlocks (Pro class, Bad Lands, Mardi Gras, bonus tracks).' },
  { name: 'Showdown', status: 'finished',
    pt: 'Duelo 1 contra 1 com escolha do adversário, do início aos resultados.',
    en: 'One-on-one duel with opponent selection, from start to results.' },
  { name: 'Time Trial', status: 'finished',
    pt: 'Contra o relógio; usado como teste de referência da física a 30 e 60 fps.',
    en: 'Against the clock; used as the physics reference test at 30 and 60 fps.' },
  { name: 'Race Options', status: 'finished',
    pt: 'Número de carros, equipes, voltas e seleção de oponentes respeitados na corrida.',
    en: 'Vehicle count, teams, laps and opponent selection are honored in the race.' },
  { name: 'Showcase', status: 'finished',
    pt: 'Vídeos originais (créditos, Cyber Athlete, NASCAR 2000) tocam no port.',
    en: 'Original videos (credits, Cyber Athlete, NASCAR 2000) play in the port.' },
  { name: 'Game Options', status: 'finished',
    pt: 'Menu de áudio, nome, recordes, controle e dicas abre e navega.',
    en: 'Audio, name, records, controller and hints menu opens and navigates.' },
  { name: 'Memory Card', status: 'finished',
    pt: 'Salvar depois da corrida, sobrescrever e carregar em Load and Save: recordes e progresso voltam num novo boot.',
    en: 'Saving after a race, overwriting and loading from Load and Save: records and progress come back on a new boot.' },
  { name: '2 Players', status: 'racing',
    pt: 'O jogo pede um controle na porta 2; falta mapear o segundo controle no host.',
    en: 'The game asks for a controller in port 2; the host still has to map a second controller.' },
];
