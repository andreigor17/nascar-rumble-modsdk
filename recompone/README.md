# Port nativo via RecompOne (Trilha B)

Ponte **Ghidra → RecompOne**: o MIPS do NASCAR Rumble é recompilado para C# nativo usando o
nosso mapa de funções do Ghidra. Estado: **recompila e compila (0 erros)**; o boot funciona
onde a janela GLFW/OpenGL abre — **no macOS trava em `glfwSetWindowPos` (janela nula); usar
Windows** (ver `docs/ANALISE_RECOMPONE.md`).

## Arquivos versionados
- `nascar_funcmap.json` — 1855 funções do EXE (gerado de `ghidra_out/functions.csv`).
- `nascar.json` — config do RecompOne (disco + funcMap + `main=800a5440`, sem overlays).
- `host/` — projeto .NET que junta o `RecompOne.Runtime` + o C# gerado e chama `Entry.Run`.
- `Recompiled/` é **gerado** (git-ignored) — recriado ao rodar o recompilador.

## Rodar (Windows)
```powershell
# 1) .NET 10 SDK instalado (https://dotnet.microsoft.com/download)
# 2) clonar o RecompOne ao lado (tools/RecompOne) e compilar
git clone https://github.com/BlackLabelHQ/RecompOne tools/RecompOne
dotnet build tools/RecompOne/RecompOne.Recompiler -c Release
# 3) gerar o C# a partir do nosso funcMap
dotnet tools/RecompOne/RecompOne.Recompiler/bin/Release/net10.0/recompone.dll recompone/nascar.json
# 4) compilar e rodar o host (passe o caminho do .cue como argumento)
dotnet build recompone/host -c Release
recompone/host/bin/Release/net10.0/NascarRumbleNative.exe "CAMINHO\NASCAR Rumble (USA).cue"
```
> Ajuste os caminhos em `nascar.json` (`cue`, `funcMap`) e no `host.csproj` (ProjectReference)
> conforme a sua estrutura. No Windows, a janela GLFW deve abrir normalmente.
