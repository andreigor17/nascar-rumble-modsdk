export type Tool = { file: string; pt: string; en: string };

export const TOOLS: Tool[] = [
  { file: 'scripts/iso_tree.py', pt: 'Parser de ISO9660 (Mode2/2352): lista, extrai e gera o ISO_TREE.', en: 'ISO9660 (Mode2/2352) parser: lists, extracts and builds the ISO_TREE.' },
  { file: 'scripts/chunk_explorer.py', pt: 'Explorador dos chunks do container EA (CTRL/SHOC/...).', en: 'Explorer for EA container chunks (CTRL/SHOC/...).' },
  { file: 'scripts/extract_resources.py', pt: 'Remonta recursos nomeados de um .TRK/GlblData (Cpag, Ctrk, Cobj...).', en: 'Reassembles named resources from a .TRK/GlblData (Cpag, Ctrk, Cobj...).' },
  { file: 'scripts/decode_lsc.py', pt: 'Decodifica telas de loading .LSC (MDEC) para PNG.', en: 'Decodes .LSC loading screens (MDEC) to PNG.' },
  { file: 'scripts/decode_cpag.py', pt: 'Decodifica páginas de textura Cpag (4bpp + CLUT) para PNG.', en: 'Decodes Cpag texture pages (4bpp + CLUT) to PNG.' },
  { file: 'scripts/plot_track.py', pt: 'Extrai e plota o traçado (linha central) de uma pista Ctrk.', en: 'Extracts and plots the centerline of a Ctrk track.' },
  { file: 'scripts/exe_strings.py', pt: 'Extrai strings do PS-X EXE já com o endereço de RAM.', en: 'Extracts PS-X EXE strings with their RAM address.' },
  { file: 'scripts/ghidra/export_analysis.py', pt: 'Pipeline PyGhidra: analisa o EXE e exporta funções + decompilado.', en: 'PyGhidra pipeline: analyzes the EXE and exports functions + decompilation.' },
  { file: 'scripts/ghidra/decompile_funcs.py', pt: 'Decompila funções específicas sob demanda (headless).', en: 'Decompiles specific functions on demand (headless).' },
];
