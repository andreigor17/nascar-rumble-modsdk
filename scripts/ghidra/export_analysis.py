#!/usr/bin/env python3
"""
export_analysis.py — Dirige o Ghidra (headless, via PyGhidra) para importar e analisar
o SLUS_010.68 e EXPORTAR tudo para arquivos texto que podemos ler/gerar sem GUI:

  ghidra_out/functions.csv      — todas as funções (endereço, nome, tamanho)
  ghidra_out/strings_xref.csv   — strings definidas + função que as referencia
  ghidra_out/decomp_all.c       — pseudocódigo C de TODAS as funções (com cabeçalho de endereço)

Reusa o projeto em ghidra/NASCAR_headless: a 1ª execução analisa (lento);
as seguintes reabrem o programa já analisado (rápido).

Uso:
  source .venv-ghidra/bin/activate
  GHIDRA_INSTALL_DIR=/opt/homebrew/Cellar/ghidra/12.1.2/libexec \
    python scripts/ghidra/export_analysis.py
"""
import os
import csv
from pathlib import Path

import pyghidra

REPO = Path(__file__).resolve().parents[2]
EXE = REPO / "extracted" / "SLUS_010.68"
OUT = REPO / "ghidra_out"
PROJ_DIR = REPO / "ghidra"
PROJ_NAME = "NASCAR_headless"


def main():
    OUT.mkdir(exist_ok=True)
    with pyghidra.open_program(
        str(EXE),
        project_location=str(PROJ_DIR),
        project_name=PROJ_NAME,
        analyze=True,
    ) as flat:
        program = flat.getCurrentProgram()
        from ghidra.app.decompiler import DecompInterface
        from ghidra.util.task import ConsoleTaskMonitor

        base = program.getImageBase()
        print(f"programa: {program.getName()}  base={base}")

        fm = program.getFunctionManager()
        funcs = list(fm.getFunctions(True))
        print(f"funções: {len(funcs)}")

        # 1) functions.csv
        with open(OUT / "functions.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["address", "name", "size", "is_thunk"])
            for fn in funcs:
                w.writerow([
                    f"0x{fn.getEntryPoint().getOffset():08x}",
                    fn.getName(),
                    fn.getBody().getNumAddresses(),
                    fn.isThunk(),
                ])

        # 2) strings_xref.csv
        listing = program.getListing()
        refmgr = program.getReferenceManager()
        with open(OUT / "strings_xref.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["str_addr", "text", "xref_from", "in_function"])
            data_iter = listing.getDefinedData(True)
            for data in data_iter:
                val = data.getValue()
                dt = data.getDataType().getName().lower()
                if val is None or ("string" not in dt and "char" not in dt):
                    continue
                text = str(val)
                if len(text) < 3:
                    continue
                addr = data.getAddress()
                refs = refmgr.getReferencesTo(addr)
                wrote = False
                for r in refs:
                    src = r.getFromAddress()
                    fn = fm.getFunctionContaining(src)
                    w.writerow([
                        f"0x{addr.getOffset():08x}",
                        text.replace("\n", "\\n")[:120],
                        f"0x{src.getOffset():08x}",
                        fn.getName() if fn else "",
                    ])
                    wrote = True
                if not wrote:
                    w.writerow([f"0x{addr.getOffset():08x}",
                                text.replace("\n", "\\n")[:120], "", ""])

        # 3) decomp_all.c
        from ghidra.app.decompiler import DecompileOptions
        decomp = DecompInterface()
        decomp.setOptions(DecompileOptions())
        decomp.toggleCCode(True)
        decomp.toggleSyntaxTree(True)
        decomp.setSimplificationStyle("decompile")
        assert decomp.openProgram(program), "decompiler não abriu o programa"
        monitor = ConsoleTaskMonitor()
        with open(OUT / "decomp_all.c", "w") as f:
            for i, fn in enumerate(funcs):
                ep = fn.getEntryPoint().getOffset()
                res = decomp.decompileFunction(fn, 60, monitor)
                f.write(f"\n/* ===== 0x{ep:08x}  {fn.getName()} ===== */\n")
                if res and res.decompileCompleted():
                    f.write(res.getDecompiledFunction().getC())
                else:
                    f.write(f"// (falha ao decompilar {fn.getName()})\n")
                if i % 100 == 0:
                    print(f"  decompiladas {i}/{len(funcs)}")
        print("OK -> ghidra_out/{functions.csv,strings_xref.csv,decomp_all.c}")


if __name__ == "__main__":
    main()
