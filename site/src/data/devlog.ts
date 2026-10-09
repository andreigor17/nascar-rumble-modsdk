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
    slug: 'sessao-017-memory-card',
    date: '2026-10-08',
    session: '017',
    tag: 'Port nativo',
    image: '/shots/memcard-saved.jpg',
    pt: {
      title: 'Memory card: o progresso agora fica salvo',
      summary:
        'Salvar depois da corrida não trava mais em “Checking...”. O port grava no memory card virtual, mostra “Saved Successfully” e, num novo boot, carrega o save de volta com recordes e progresso.',
      points: [
        'O driver de memory card do jogo funciona por eventos da BIOS: um tipo avisa que o cartão respondeu (SwCARD) e outro que um setor de 128 bytes foi transferido (HwCARD). O runtime disparava os dois em toda operação, e o jogo entende um SwCARD no meio de uma leitura ou gravação como “aborta e começa de novo”. Resultado: a leitura do diretório nunca terminava e a tela ficava em “Checking...”.',
        'A referência foi o OpenBIOS, a BIOS do emulador PCSX-Redux: leitura e gravação de setor geram só HwCARD, e a consulta ao cartão gera SwCARD e depois HwCARD. Isso também explica um detalhe do jogo: ele ignora o primeiro HwCARD de cada transferência, justamente o que chega logo depois do SwCARD que a iniciou.',
        'Segundo ajuste: no console cada setor leva alguns milissegundos, e a tela de Load só percebe o fim do carregamento vendo o status “carregando” mudar entre uma consulta e outra. No port as 60 leituras terminavam no mesmo quadro e a tela ficava em “Loading...” para sempre; agora cada setor conclui em um quadro.',
        'Testado no port: salvar num cartão vazio após uma Single Race, sobrescrever um save existente e carregar em Game Options › Load and Save. O recorde de Copper Canyon da sessão anterior volta depois do Load.',
        'O save ocupa 1 bloco (8 KB) no memory card virtual, com o nome original BASLUS-01068NASCRMBL.',
      ],
    },
    en: {
      title: 'Memory card: progress now gets saved',
      summary:
        'Saving after a race no longer hangs at “Checking...”. The port writes to the virtual memory card, shows “Saved Successfully” and, on a new boot, loads the save back with records and progress.',
      points: [
        'The game’s memory card driver runs on BIOS events: one kind says the card answered (SwCARD), another that a 128-byte sector was transferred (HwCARD). The runtime fired both for every operation, and the game reads a SwCARD in the middle of a read or write as “abort and start over”. So the directory read never finished and the screen stayed at “Checking...”.',
        'The reference was OpenBIOS, the BIOS of the PCSX-Redux emulator: sector reads and writes raise only HwCARD, and the card query raises SwCARD and then HwCARD. That also explains a detail in the game: it ignores the first HwCARD of every transfer, which is exactly the one arriving right after the SwCARD that started it.',
        'Second fix: on the console each sector takes a few milliseconds, and the Load screen only notices the load is done by seeing the “loading” status change between polls. In the port all 60 reads finished within one frame and the screen stayed at “Loading...” forever; now each sector completes in one frame.',
        'Tested in the port: saving to a blank card after a Single Race, overwriting an existing save, and loading from Game Options › Load and Save. The Copper Canyon record from the previous session comes back after Load.',
        'The save takes 1 block (8 KB) on the virtual memory card, under the original name BASLUS-01068NASCRMBL.',
      ],
    },
  },
  {
    slug: 'sessao-016-campeonato-completo',
    date: '2026-10-08',
    session: '016',
    tag: 'Port nativo',
    image: '/shots/standings.jpg',
    pt: {
      title: 'Bandeirada: corrida completa e campeonato inteiro no port nativo',
      summary:
        'O port nativo agora vai do boot até o fim de um campeonato: três etapas, pontos, classificação geral e os desbloqueios originais. Ganhou também um lançador no estilo do jogo e um contador de FPS.',
      points: [
        'Corrida completa: tempos de volta da IA iguais ao PS1 (±0,4%) a 30 e a 60 fps, com chegada, tela de resultados e retorno ao menu.',
        'Championship: nome do piloto, copa Gold Rush com Copper Canyon, Golden Rule e Silver Falls, grid invertido pela classificação, pontos por etapa e, no fim, desbloqueio da classe Pro, das regiões Bad Lands e Mardi Gras e de pistas bônus.',
        'Showdown, Time Trial, Race Options, Game Options e os vídeos do Showcase também funcionam.',
        'Para percorrer o campeonato inteiro de forma automática criamos um atalho de teste (RUMBLE_QUICK_FINISH) que põe o carro do jogador na última volta; por isso os tempos do “77” nas capturas são curtos. A corrida em si roda do mesmo jeito sem o atalho.',
        'Lançador antes do boot, desenhado como o menu do jogo e com a arte de abertura lida do seu próprio disco: 30 ou 60 fps, contador de FPS no canto superior direito e modo debug.',
        'Ainda não: salvar no memory card trava em “Checking...” e o modo 2 jogadores pede um segundo controle que o host ainda não mapeia.',
      ],
    },
    en: {
      title: 'Checkered flag: a complete race and a whole championship in the native port',
      summary:
        'The native port now goes from boot to the end of a championship: three rounds, points, overall standings and the original unlocks. It also gained a game-styled launcher and an FPS counter.',
      points: [
        'Complete race: AI lap times match the PS1 (±0.4%) at 30 and 60 fps, with the finish, the results screen and the return to the menu.',
        'Championship: driver name, the Gold Rush cup with Copper Canyon, Golden Rule and Silver Falls, a grid reversed by the standings, points per round and, at the end, the Pro class, the Bad Lands and Mardi Gras locales and bonus tracks unlocked.',
        'Showdown, Time Trial, Race Options, Game Options and the Showcase videos work too.',
        'To drive the whole championship automatically we added a test shortcut (RUMBLE_QUICK_FINISH) that puts the player’s car on its last lap; that is why the “77” times in the captures are short. The race itself runs the same without it.',
        'A launcher before boot, drawn like the game menu with the title art read from your own disc: 30 or 60 fps, an FPS counter in the top-right corner and debug mode.',
        'Not yet: saving to the memory card hangs at “Checking...”, and 2 Players asks for a second controller the host does not map yet.',
      ],
    },
  },
  {
    slug: 'sessao-015-demo-estavel',
    date: '2026-10-08',
    session: '015',
    tag: 'Port nativo',
    image: '/gallery/native-main-menu.png',
    pt: {
      title: 'Intro, menu e demo estável: os carros agora correm no chão',
      summary:
        'O port nativo reproduz a intro inteira, chega ao menu, aceita o controle e roda a demo de corrida com os carros apoiados na pista, no ritmo do tempo real.',
      points: [
        'A intro completa toca com áudio, pode ser pulada como no PS1 e leva ao carregamento e ao menu principal, que já responde ao teclado.',
        'Os carros flutuavam e eram lançados ao céu. Um verificador diferencial executa o código MIPS original ao lado do código traduzido e provou que a tradução estava certa; o defeito era no comando OP da GTE do runtime, que reaproveitava um registrador já sobrescrito e corrompia a altura do terreno.',
        'Com a GTE corrigida, os seis carros nascem no grid na mesma altura e percorrem a pista sem decolar.',
        'A corrida passou de ~12 para ~33 quadros por segundo ao eliminar uma espera da GPU a cada lote de desenho no macOS, e o relógio da corrida agora segue o tempo real, como no console.',
        'Próximo marco: validar a IA, jogar uma corrida manual completa e conferir HUD, áudio e retorno ao menu.',
      ],
    },
    en: {
      title: 'Intro, menu, and a stable demo: cars now race on the ground',
      summary:
        'The native port plays the full intro, reaches the menu, accepts input, and runs the race demo with cars resting on the track at real-time speed.',
      points: [
        'The full intro plays with audio, can be skipped as on the PS1, and leads to the loading screen and the main menu, which responds to the keyboard.',
        'Cars used to float and get launched into the sky. A differential checker runs the original MIPS code next to the translated code and proved the translation correct; the bug was in the runtime GTE OP command, which reused an already-overwritten register and corrupted terrain height.',
        'With the GTE fixed, all six cars spawn on the grid at the same height and drive the track without taking off.',
        'Race rendering went from ~12 to ~33 frames per second by removing a per-batch GPU wait on macOS, and the race clock now follows real time, as on the console.',
        'Next milestone: validate the AI, play a complete manual race, and check the HUD, audio, and return to the menu.',
      ],
    },
  },
  {
    slug: 'sessao-014-primeiro-quadro-nativo',
    date: '2026-10-07',
    session: '014',
    tag: 'Port nativo',
    image: '/gallery/native-ea-first-frame.png',
    pt: {
      title: 'A primeira imagem do jogo apareceu no port nativo',
      summary:
        'O executável macOS ARM já abre o vídeo original de introdução e apresenta o logo da EA em sua própria janela OpenGL.',
      points: [
        'O boot atravessa tela legal, memory card e inicialização do streaming até encontrar INTRO.WVE no disco original.',
        'Callbacks cooperativos de VBlank, CD e DMA alimentam o MDEC; os primeiros quadros de 280 macroblocos chegam à GPU e aparecem na janela nativa.',
        'A reprodução avança aproximadamente 15 quadros antes de um underflow do buffer de áudio. O próximo marco é manter a intro em movimento e alcançar o menu.',
      ],
    },
    en: {
      title: 'The game’s first image is visible in the native port',
      summary:
        'The macOS ARM executable now opens the original intro video and presents the EA logo in its own OpenGL window.',
      points: [
        'Boot crosses the legal screen, memory-card flow, and streaming setup before finding INTRO.WVE on the original disc.',
        'Cooperative VBlank, CD, and DMA callbacks feed MDEC; the first 280-macroblock frames reach the GPU and appear in the native window.',
        'Playback advances for roughly 15 frames before an audio-buffer underflow. The next milestone is continuous intro playback and reaching the menu.',
      ],
    },
  },
  {
    slug: 'sessao-013-cd-mdec-e-tela-legal',
    date: '2026-10-07',
    session: '013',
    tag: 'Port nativo',
    pt: {
      title: 'O boot nativo já lê e decodifica a tela legal',
      summary:
        'O bloqueio do CD foi vencido: o executável entrega todos os setores da abertura e decodifica as duas imagens originais da tela legal.',
      points: [
        'LEGAL.LSC é lido por completo em 18 setores, com callbacks de CD e DMA funcionando sem recursão ou estouro de pilha.',
        'As duas imagens passam pelo MDEC: 160 macroblocos e 30.720 palavras de saída em cada quadro, seguidos da transferência para a GPU.',
        'O próximo bloqueio está isolado no agendamento cooperativo de VBlank e memory card antes do loop normal; intro e menu ainda não foram confirmados visualmente.',
      ],
    },
    en: {
      title: 'Native boot now reads and decodes the legal screen',
      summary:
        'The CD blocker is cleared: the executable delivers every opening sector and decodes both original legal-screen images.',
      points: [
        'LEGAL.LSC is fully read across 18 sectors, with CD callbacks and DMA working without recursion or stack overflow.',
        'Both images pass through MDEC: 160 macroblocks and 30,720 output words per frame, followed by a GPU transfer.',
        'The next blocker is isolated to cooperative VBlank and memory-card scheduling before the normal frame loop; intro and menu are not visually confirmed yet.',
      ],
    },
  },
  {
    slug: 'sessao-012-janela-nativa-e-boot-original',
    date: '2026-10-07',
    session: '012',
    tag: 'Port nativo',
    pt: {
      title: 'A janela nativa abre e o boot original já começou',
      summary:
        'O executável macOS ARM agora abre uma janela própria, entra no jogo e avança até a primeira leitura da abertura — ainda sem imagem ou menu.',
      points: [
        'A recompilação estática abre uma janela OpenGL de 1280×748 no macOS, entra no main e inicializa memória, controles, GPU, áudio e CD.',
        'O jogo encontra CW/OPENING/LEGAL.LSC no disco original. O bloqueio atual está no fluxo assíncrono ReadN do CD, antes do primeiro quadro visível.',
        'A prioridade agora é reproduzir o jogo original até menu e corrida completa. Mods e melhorias ficam desligados por padrão até essa base estar estável.',
      ],
    },
    en: {
      title: 'The native window opens and the original boot has begun',
      summary:
        'The macOS ARM executable now opens its own window, enters the game and reaches the first opening read — still without a visible image or menu.',
      points: [
        'The static recompile opens a 1280×748 OpenGL window on macOS, enters main, and initializes memory, input, GPU, audio, and CD.',
        'The game finds CW/OPENING/LEGAL.LSC on the original disc. The current blocker is the asynchronous CD ReadN flow, before the first visible frame.',
        'The priority is now original-game parity through the menu and a complete race. Mods and enhancements stay off by default until that base is stable.',
      ],
    },
  },
  {
    slug: 'sessao-011-port-nativo',
    date: '2026-07-22',
    session: '011',
    tag: 'Port nativo',
    pt: {
      title: 'O jogo virou código nativo: 188 mil linhas de C#',
      summary:
        'Ligamos a nossa engenharia reversa ao recompilador RecompOne e transformamos o NASCAR Rumble num executável nativo que compila sem erros.',
      points: [
        'O nosso mapa de 1855 funções (do Ghidra) alimentou o RecompOne, que traduziu o MIPS do jogo em C# — main.cs com 188.902 linhas.',
        'O build nativo compilou com 0 erros. A ponte "engenharia reversa → executável sem emulador" funciona de ponta a ponta.',
        'Naquele momento o boot ainda travava na criação da janela gráfica no macOS; esse bloqueio foi superado na sessão 012.',
      ],
    },
    en: {
      title: 'The game became native code: 188k lines of C#',
      summary:
        'We connected our reverse engineering to the RecompOne recompiler and turned NASCAR Rumble into a native executable that compiles cleanly.',
      points: [
        'Our 1855-function map (from Ghidra) fed RecompOne, which translated the game’s MIPS into C# — a 188,902-line main.cs.',
        'The native build compiled with 0 errors. The "reverse engineering → run without emulator" bridge works end to end.',
        'At that point boot still crashed during graphics window creation on macOS; session 012 has since cleared that blocker.',
      ],
    },
  },
  {
    slug: 'sessao-010-emulador-e-carros',
    date: '2026-07-22',
    session: '010',
    tag: 'Emulador + Carros',
    pt: {
      title: 'Controle total do jogo e o catálogo dos 168 carros',
      summary:
        'Passamos a controlar o jogo sozinhos (tela, controle e memória) e mapeamos os primeiros dados vivos + o catálogo completo de carros.',
      points: [
        'Controle autônomo via PCSX-Redux: vemos a tela, apertamos os botões e lemos/escrevemos a memória — navegamos e corremos por conta própria.',
        'Primeiros endereços vivos: contador de voltas e velocidade. Classes confirmadas: Rookie 160 / Pro 170 / Elite 180; power-up de velocidade = +20.',
        'Catálogo completo: 168 carros = 56 pilotos × 3 classes, cruzado com o roster do executável.',
      ],
    },
    en: {
      title: 'Full game control and the 168-car catalog',
      summary:
        'We now control the game ourselves (screen, input and memory) and mapped the first live data + the complete car catalog.',
      points: [
        'Autonomous control via PCSX-Redux: we see the screen, press the buttons and read/write memory — navigating and racing on our own.',
        'First live addresses: lap counter and speed. Classes confirmed: Rookie 160 / Pro 170 / Elite 180; speed power-up = +20.',
        'Complete catalog: 168 cars = 56 drivers × 3 classes, cross-referenced with the executable roster.',
      ],
    },
  },
  {
    slug: 'sessao-009-catalogo-carros',
    date: '2026-07-22',
    session: '009',
    tag: 'Carros',
    image: '/cars/petty-43.png',
    pt: {
      title: 'Catálogo de carros e as 171 liveries da NASCAR',
      summary:
        'Publicamos a página dos 32 carros do grid e descobrimos que o disco guarda todas as pinturas reais da NASCAR da época.',
      points: [
        'Nova página "Carros": o roster completo (piloto, número, rating e classe) com barras de desempenho.',
        'O disco tem 171 liveries — muito além dos 32 selecionáveis: Jeff Gordon #24 (DuPont), Terry Labonte #5 (Kellogg’s), e mais.',
        'Duplas confirmadas por número: Richard Petty #43 e Stacy Compton #86. Ligar cada piloto à pintura exata é o próximo passo.',
      ],
    },
    en: {
      title: 'Car catalog and the 171 NASCAR liveries',
      summary:
        'We published the 32-car grid page and found the disc holds every real NASCAR paint of the era.',
      points: [
        'New "Cars" page: the full roster (driver, number, rating and class) with performance bars.',
        'The disc has 171 liveries — far beyond the 32 selectable: Jeff Gordon #24 (DuPont), Terry Labonte #5 (Kellogg’s), and more.',
        'Number-confirmed pairs: Richard Petty #43 and Stacy Compton #86. Linking each driver to their exact livery is next.',
      ],
    },
  },
  {
    slug: 'sessao-008-roster-e-stats',
    date: '2026-07-21',
    session: '008',
    tag: 'Stats',
    pt: {
      title: 'O roster: 32 carros com número, rating e classe',
      summary:
        'Encontramos no executável a tabela de carros do jogo — com os pilotos reais, seus números e desempenho.',
      points: [
        'Tabela de 32 structs (12 bytes cada): nome, número do carro, índice do modelo, rating e classe.',
        'As lendas dominam: Richard Petty (rating 63), Cale Yarborough (62), Benny Parsons (60). Novatos ficam ~20.',
        'O índice do modelo liga cada piloto à sua pintura 3D — base para um futuro Car Editor.',
      ],
    },
    en: {
      title: 'The roster: 32 cars with number, rating and class',
      summary:
        'We found the game’s car table in the executable — with the real drivers, their numbers and performance.',
      points: [
        'Table of 32 structs (12 bytes each): name, car number, model index, rating and class.',
        'The legends dominate: Richard Petty (rating 63), Cale Yarborough (62), Benny Parsons (60). Rookies sit ~20.',
        'The model index links each driver to their 3D livery — groundwork for a future Car Editor.',
      ],
    },
  },
  {
    slug: 'sessao-007-carros',
    date: '2026-07-21',
    session: '007',
    tag: 'Carros',
    image: '/gallery/car-livery.png',
    pt: {
      title: 'Os carros: 171 pinturas extraídas do jogo',
      summary:
        'Abrimos o arquivo de dados globais e encontramos as pinturas de todos os carros — incluindo pilotos reais da NASCAR.',
      points: [
        'O GlblData.psx são 172 containers concatenados: fontes, objetos e a grade de carros.',
        'Extraímos 171 páginas de textura — as liveries dos carros — mais modelos (Cobj) e stats (Ceng).',
        'Confirmado visualmente: o #43 do Richard Petty (patrocínio EXIDE) e outros esquemas reais.',
      ],
    },
    en: {
      title: 'The cars: 171 liveries extracted from the game',
      summary:
        'We opened the global data file and found every car’s paint scheme — including real NASCAR drivers.',
      points: [
        'GlblData.psx is 172 concatenated containers: fonts, objects and the car grid.',
        'We extracted 171 texture pages — the car liveries — plus models (Cobj) and stats (Ceng).',
        'Visually confirmed: Richard Petty’s #43 (EXIDE sponsor) and other real schemes.',
      ],
    },
  },
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
