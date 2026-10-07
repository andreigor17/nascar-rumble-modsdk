# Port nativo via RecompOne (Trilha B)

Ponte **Ghidra → RecompOne**: o MIPS do NASCAR Rumble é recompilado para C# nativo usando o
nosso mapa de funções do Ghidra. Estado: **recompila e compila (0 erros)**; no macOS ARM a janela
agora abre com o patch OpenGL 4.1, o jogo entra no `main`, inicializa os subsistemas e localiza
`CW/OPENING/LEGAL.LSC`. Ainda trava no primeiro `ReadN` do CD, antes de mostrar a tela legal,
intro ou menu (ver `docs/ANALISE_RECOMPONE.md`).

## Arquivos versionados
- `nascar_funcmap.json` — 1855 funções do EXE (gerado de `ghidra_out/functions.csv`).
- `nascar.json` — config do RecompOne (disco + funcMap + `main=800a5440`, sem overlays).
- `host/` — projeto .NET que junta o `RecompOne.Runtime` + o C# gerado e chama `Entry.Run`.
- `Recompiled/` é **gerado** (git-ignored) — recriado ao rodar o recompilador.

## Compilar e rodar no macOS

Com .NET 10 e a cópia legal nos caminhos do projeto:

```sh
make native-build
make native-run
```

Para registrar chamadas de BIOS/SDK/CD enquanto investigamos o boot:

```sh
make native-trace
```

`scripts/build_native.py` valida o commit fixado do RecompOne, aplica
`patches/recompone-macos.patch`, gera os alvos auxiliares do dispatcher, recompila o jogo e produz
`host/bin/Release/net10.0/NascarRumbleNative`.

## Rodar no Windows
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
> conforme a sua estrutura.
