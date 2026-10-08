# Port nativo via RecompOne (Trilha B)

Ponte **Ghidra → RecompOne**: o MIPS do NASCAR Rumble é recompilado para C# nativo usando o
nosso mapa de funções do Ghidra. Estado: **recompila e compila (0 erros)**; no macOS ARM a janela
abre com OpenGL 4.1, reproduz a intro, aceita o skip original, conclui o carregamento, chega ao menu
e entra em demo/corrida manual. A flutuação dos carros foi rastreada até um bug no comando OP da
GTE do runtime (corrigido no patch local); com ele os carros nascem e correm apoiados na pista. O
handoff técnico completo está em `notes/SESSION_011.md`.

O objetivo desta trilha é executar primeiro o jogo **original**. O carregador de mods fica
desligado, a menos que `RUMBLE_ENABLE_MODS=1` seja definido explicitamente; esse modo não faz parte
do gate atual. O usuário fornece seu próprio CUE/BIN legal, que nunca é incorporado ao executável.

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

## Verificação diferencial (`RUMBLE_SHADOW=1`)

`host/ShadowCpu.cs` executa o MIPS original (residente na RAM emulada) num interpretador R3000
antes de cada chamada recompilada de `FUN_80064acc`, `FUN_80065488` e `FUN_80056c6c`, com escritas
num overlay e a GTE salva/restaurada. Depois compara V0 e as escritas com o C# gerado em três
variantes: com load-delay, sem load-delay e com uma GTE mínima independente (só OP). Divergências
aparecem como `[shadow] MISMATCH`; sem a variável, os hooks são inertes. Para checar outra função,
registrar pre/post em `nascar.json` chamando `ShadowCpu.Pre/Post` com o endereço dela.

```sh
RUMBLE_SHADOW=1 RUMBLE_NATIVE_TRACE=1 make native-run
```

## Controles e desempenho

Teclado padrão (`settings.json`, criado pelo runtime): Z = Cross (acelerar/confirmar), A = Square
(frear/ré), X = Circle (voltar), S = Triangle, Q/W = L1/R1, E/R = L2/R2, Enter = Start, Shift
direito = Select, setas = direcional. Para avaliar jogabilidade ou FPS, rodar **sem**
`RUMBLE_SHADOW`; `RUMBLE_NATIVE_TRACE=2` registra o timing de todos os quadros da corrida.
