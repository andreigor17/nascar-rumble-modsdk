#!/usr/bin/env python3
"""
decompile_funcs.py — Decompila funções específicas (por endereço) do projeto já analisado
e grava cada uma em ghidra_out/func_<addr>.c. Setup correto do DecompInterface.

Uso:
  source .venv-ghidra/bin/activate
  GHIDRA_INSTALL_DIR=/opt/homebrew/Cellar/ghidra/12.1.2/libexec \
    python scripts/ghidra/decompile_funcs.py 0x8002baa8 0x80043520 0x800921a0 0x80079814
"""
import sys
from pathlib import Path
import pyghidra

REPO = Path("/opt/Projetos/rumble")
OUT = REPO / "ghidra_out"


def main(addrs):
    OUT.mkdir(exist_ok=True)
    with pyghidra.open_program(
        str(REPO / "extracted" / "SLUS_010.68"),
        project_location=str(REPO / "ghidra"),
        project_name="NASCAR_headless",
        analyze=False,
    ) as flat:
        program = flat.getCurrentProgram()
        from ghidra.app.decompiler import DecompInterface, DecompileOptions
        from ghidra.util.task import ConsoleTaskMonitor

        af = program.getAddressFactory()
        fm = program.getFunctionManager()

        decomp = DecompInterface()
        opts = DecompileOptions()
        decomp.setOptions(opts)
        decomp.toggleCCode(True)
        decomp.toggleSyntaxTree(True)
        decomp.setSimplificationStyle("decompile")
        ok = decomp.openProgram(program)
        print("openProgram:", ok, "| lastMessage:", decomp.getLastMessage())

        monitor = ConsoleTaskMonitor()
        for a in addrs:
            addr = af.getAddress(a)
            fn = fm.getFunctionContaining(addr)
            if fn is None:
                print(f"{a}: nenhuma função"); continue
            res = decomp.decompileFunction(fn, 180, monitor)
            if res.decompileCompleted():
                c = res.getDecompiledFunction().getC()
                p = OUT / f"func_{a}.c"
                p.write_text(c)
                print(f"{a} {fn.getName()} -> {p.name} ({len(c)} chars)")
            else:
                print(f"{a} {fn.getName()}: FALHOU -> {res.getErrorMessage()}")


if __name__ == "__main__":
    main(sys.argv[1:] or ["0x8002baa8"])
