export type Phase = { n: number; status: 'done' | 'doing' | 'todo'; pt: string; en: string; pt_d: string; en_d: string };

export const ROADMAP: Phase[] = [
  { n: 1, status: 'done', pt: 'Ambiente', en: 'Environment',
    pt_d: 'Ghidra, PyGhidra, emuladores, Python e Git.', en_d: 'Ghidra, PyGhidra, emulators, Python and Git.' },
  { n: 2, status: 'done', pt: 'Pesquisa da ISO', en: 'ISO research',
    pt_d: 'ISO_TREE.md com os 108 arquivos mapeados.', en_d: 'ISO_TREE.md with all 108 files mapped.' },
  { n: 3, status: 'doing', pt: 'ISO Explorer', en: 'ISO Explorer',
    pt_d: 'Ferramentas de extração (parser + extrator de recursos).', en_d: 'Extraction tools (parser + resource extractor).' },
  { n: 4, status: 'doing', pt: 'Análise do executável', en: 'Executable analysis',
    pt_d: '2008 funções exportadas; funções-chave nomeadas.', en_d: '2008 functions exported; key functions named.' },
  { n: 5, status: 'todo', pt: 'Mapa da RAM', en: 'RAM map',
    pt_d: 'Localizar structs vivas (carro, IA, power-ups).', en_d: 'Locate live structs (car, AI, power-ups).' },
  { n: 6, status: 'doing', pt: 'Formatos de arquivo', en: 'File formats',
    pt_d: 'Container, .LSC, texturas e pistas decodificados.', en_d: 'Container, .LSC, textures and tracks decoded.' },
  { n: 7, status: 'todo', pt: 'Visualizadores', en: 'Viewers',
    pt_d: 'Texture Viewer, Track Viewer 3D, Model Viewer.', en_d: 'Texture Viewer, 3D Track Viewer, Model Viewer.' },
  { n: 8, status: 'todo', pt: 'Jogabilidade', en: 'Gameplay',
    pt_d: 'Física, IA, power-ups e HUD.', en_d: 'Physics, AI, power-ups and HUD.' },
  { n: 9, status: 'todo', pt: 'SDK de escrita', en: 'Authoring SDK',
    pt_d: 'Editores + reconstrução de ISO (Patch Builder).', en_d: 'Editors + ISO rebuild (Patch Builder).' },
  { n: 10, status: 'todo', pt: 'Port nativo', en: 'Native port',
    pt_d: 'Duas trilhas: RecompOne (rápida) e decomp matching.', en_d: 'Two tracks: RecompOne (fast) and matching decomp.' },
];
