import type { Lang } from '../consts';

export interface DevlogEntry {
  slug: string;
  date: string;         // ISO
  session: string;      // "001"
  tag: string;          // curto, ex.: "Formatos"
  image?: string;       // caminho em /public (sem base)
  pt: { title: string; summary: string; points: string[] };
  en: { title: string; summary: string; points: string[] };
}

export const DEVLOG: DevlogEntry[] = [
  {
    slug: 'sessao-006-texturas-coloridas',
    date: '2026-07-21',
    session: '006',
    tag: 'Texturas',
    image: '/gallery/texture-atlas.png',
    pt: {
      title: 'Texturas em cores: o atlas do jogo decodificado',
      summary:
        'Descobrimos como o jogo organiza as paletas por região e agora extraímos as texturas nas cores corretas.',
      points: [
        'Cada página de textura é um atlas com dezenas de regiões — cada uma com sua própria paleta de 16 cores.',
        'Decodificamos a tabela de regiões (tReg): retângulo + índice de paleta por sub-textura.',
        'Resultado: o logo "NASCAR RUMBLE", pneus, grama e asfalto aparecem coloridos. Primeiro Texture Viewer funcional.',
      ],
    },
    en: {
      title: 'Textures in color: the game atlas decoded',
      summary:
        'We found how the game organizes palettes per region and now extract textures in their correct colors.',
      points: [
        'Each texture page is an atlas with dozens of regions — each with its own 16-color palette.',
        'We decoded the region table (tReg): rectangle + palette index per sub-texture.',
        'Result: the "NASCAR RUMBLE" logo, tires, grass and asphalt appear in color. First working Texture Viewer.',
      ],
    },
  },
  {
    slug: 'sessao-005-site-e-formatos',
    date: '2026-07-21',
    session: '005',
    tag: 'Formatos + Site',
    image: '/gallery/track-jt3.png',
    pt: {
      title: 'Texturas, geometria de pista e o site do projeto',
      summary:
        'Decodificamos texturas (Cpag) e a geometria das pistas (Ctrk), e lançamos este site + backup no GitHub.',
      points: [
        'Cpag = páginas de textura com 4 mipmaps (PIX4 4bpp + CLUT 15-bit). Atlas real extraído (logo EA, "LEGEND", rodas).',
        'Ctrk = pista: TCRV (linha central), TSEG×17 (malha), TCOL (colisão), TTEX. Traçado da JT3 plotado — um oval de NASCAR.',
        'Site de apresentação em Astro (bilíngue) e repositório privado no GitHub para não perder nada.',
      ],
    },
    en: {
      title: 'Textures, track geometry and the project site',
      summary:
        'We decoded textures (Cpag) and track geometry (Ctrk), and launched this site + a GitHub backup.',
      points: [
        'Cpag = texture pages with 4 mipmaps (PIX4 4bpp + 15-bit CLUT). Real atlas extracted (EA logo, "LEGEND", wheels).',
        'Ctrk = track: TCRV (centerline), TSEG×17 (mesh), TCOL (collision), TTEX. JT3 centerline plotted — a NASCAR oval.',
        'Astro presentation site (bilingual) and a private GitHub repo so nothing is lost.',
      ],
    },
  },
  {
    slug: 'sessao-004-container-e-telas',
    date: '2026-07-21',
    session: '004',
    tag: 'Formatos',
    image: '/gallery/help1-loading.png',
    pt: {
      title: 'Container CTRL/SHOC decodificado e primeira imagem extraída',
      summary:
        'Lemos o parser do jogo no Ghidra e quebramos dois formatos: o container de recursos e as telas de loading.',
      points: [
        'Container CTRL/SHOC/SHDR/SDAT/FILL confirmado pelo parser FUN_8002a85c — extrator remonta recursos nomeados.',
        'Telas .LSC são imagens MDEC/BS v2 (magic 0x3800). Decodificamos a tela "LOADING" completa em 320×256.',
        'FILL sempre alinha a 2048 bytes → container feito para streaming por setor de CD.',
      ],
    },
    en: {
      title: 'CTRL/SHOC container decoded and first image extracted',
      summary:
        'We read the game parser in Ghidra and cracked two formats: the resource container and the loading screens.',
      points: [
        'CTRL/SHOC/SHDR/SDAT/FILL container confirmed via parser FUN_8002a85c — extractor reassembles named resources.',
        '.LSC screens are MDEC/BS v2 images (0x3800 magic). We decoded the full "LOADING" screen at 320×256.',
        'FILL always aligns to 2048 bytes → container designed for CD-sector streaming.',
      ],
    },
  },
  {
    slug: 'sessao-003-ghidra-headless',
    date: '2026-07-21',
    session: '003',
    tag: 'Ghidra',
    pt: {
      title: 'Ghidra dirigível por código (PyGhidra) — 2008 funções',
      summary:
        'Montamos um pipeline headless que analisa o executável e exporta tudo, dispensando o trabalho manual na interface.',
      points: [
        'PyGhidra importa o SLUS_010.68, analisa e exporta functions.csv, strings_xref.csv e o decompilado de 2008 funções.',
        'SDK confirmado: PsyQ 4.6. O jogo é um executável único, sem overlays — mais simples que o CTR.',
        'Funções-chave identificadas: loader de recursos, IA dos carros, runner de telas.',
      ],
    },
    en: {
      title: 'Code-driven Ghidra (PyGhidra) — 2008 functions',
      summary:
        'We built a headless pipeline that analyzes the executable and exports everything, removing the manual GUI work.',
      points: [
        'PyGhidra imports SLUS_010.68, analyzes it and exports functions.csv, strings_xref.csv and 2008 decompiled functions.',
        'SDK confirmed: PsyQ 4.6. The game is a single executable, no overlays — simpler than CTR.',
        'Key functions identified: resource loader, car AI, screen runner.',
      ],
    },
  },
  {
    slug: 'sessao-002-referencias-e-recomp',
    date: '2026-07-19',
    session: '002',
    tag: 'Pesquisa',
    pt: {
      title: 'Projetos de referência: CTR-ModSDK, ctr-native e RecompOne',
      summary:
        'Analisamos o que dá para reaproveitar de projetos de PS1 e definimos duas trilhas até um port nativo.',
      points: [
        'Adotaremos a psx-modding-toolchain (game-agnostic) como base do build/patch em vez de escrever do zero.',
        'RecompOne (recompilação estática MIPS→C#) vira a "trilha rápida" para rodar sem emulador.',
        'Trilha A (Ghidra/entendimento) alimenta a Trilha B (port) — as duas se retroalimentam.',
      ],
    },
    en: {
      title: 'Reference projects: CTR-ModSDK, ctr-native and RecompOne',
      summary:
        'We analyzed what can be reused from PS1 projects and defined two tracks toward a native port.',
      points: [
        'We will adopt the game-agnostic psx-modding-toolchain as the build/patch base instead of writing our own.',
        'RecompOne (static MIPS→C# recompilation) becomes the "fast track" to run without an emulator.',
        'Track A (Ghidra/understanding) feeds Track B (port) — the two reinforce each other.',
      ],
    },
  },
  {
    slug: 'sessao-001-iso-e-container',
    date: '2026-07-19',
    session: '001',
    tag: 'ISO',
    pt: {
      title: 'Estrutura do repositório e mapa da ISO',
      summary:
        'Primeiro contato com o disco: mapeamos os 108 arquivos e identificamos o container de recursos da EA.',
      points: [
        'Parser de ISO9660 (Mode2/2352) gera o ISO_TREE.md com LBA, tamanho, hash e formato de cada arquivo.',
        'Boot: SLUS_010.68 (PS-X EXE). GlblData.psx e as pistas .TRK usam o mesmo container de chunks.',
        'Formatos EA reconhecidos: SWVR (áudio), WVE (vídeo) — reaproveitando documentação da comunidade.',
      ],
    },
    en: {
      title: 'Repository structure and ISO map',
      summary:
        'First contact with the disc: we mapped all 108 files and identified the EA resource container.',
      points: [
        'ISO9660 (Mode2/2352) parser generates ISO_TREE.md with LBA, size, hash and format for each file.',
        'Boot: SLUS_010.68 (PS-X EXE). GlblData.psx and the .TRK tracks use the same chunk container.',
        'Recognized EA formats: SWVR (audio), WVE (video) — reusing community documentation.',
      ],
    },
  },
];

export function devlogText(entry: DevlogEntry, lang: Lang) {
  return entry[lang];
}
