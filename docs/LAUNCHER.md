# Lançador do port nativo

Menu de abertura do `NascarRumbleNative`, desenhado no mesmo estilo dos menus do jogo, para escolher
como o jogo vai rodar antes do boot: **30 ou 60 fps** e **modo debug**. Objetivo: o mantenedor (e eu)
testar o que estamos construindo sem variáveis de ambiente nem terminal.

## Análise

### Onde encaixar

`Recompiled/Entry.Run` faz `Runtime.Initialize` (abre a janela + ImGui) → `Runtime.WaitForValidDisc`
(valida o `.cue`) → monta CD, carrega o EXE e chama `start`. O lançador roda **entre a validação do
disco e o boot**: a janela e o leitor de CD já existem, nada do jogo rodou ainda. Assim as escolhas
valem desde o primeiro quadro (o ritmo da corrida é lido em `NativeHooks`).

### Visual "nos moldes do jogo"

Referência: menu principal do jogo (`site/public/gallery/native-main-menu.png`):

- fundo de arte em tela cheia com o logo **NASCAR RUMBLE**;
- caixa de menu escura translúcida, borda lilás arredondada, itens em branco;
- item selecionado: faixa **vermelho-escura** com texto **amarelo**; opções com setas `◄►` e um
  campo à direita com o valor (ex.: `Rookie`, `Some`);
- caixa de dica no canto superior direito (texto amarelo, borda lilás);
- rodapé com legendas amarelas: `✕ Advance  ↑↓ Change Selection  ←→ Change Setting`.

**Arte de fundo sem distribuir asset:** `CW/FEND/FELD.LSC` é a tela de abertura do próprio jogo
(logo + dois carros, 320×256, MDEC "BS" v2 em duas metades). O lançador **lê o arquivo do disco do
usuário em tempo de execução** (via `CueFs`) e decodifica com um decodificador BS v2 próprio em C#
(VLC MPEG-1 → desquantização → IDCT 8×8 → YCbCr→RGB). Nada de imagem do jogo entra no Git.
Validação: comparar pixel a pixel com o PNG que o `jpsxdec` gera via `scripts/decode_lsc.py`.

Fonte: a do jogo (`Cfnt` no `GLBLDATA.PSX`) ainda não foi decodificada. V1 usa uma fonte do sistema
condensada e pesada (Futura Condensed ExtraBold / Impact no macOS; ImGui padrão como fallback).

### Debug que já existe

O jogo não tem modo debug próprio (o EXE só traz `SetGraphDebug` do PsyQ). O que existe é o
conjunto do **RecompOne**, acessível pela barra superior da janela (menu **Debug**): visualizador
de VRAM, estado da CPU, editor de memória, mapa de RAM, SPU, CD, console e eventos de overlay; e do
nosso host: traces `RUMBLE_*` (`NATIVE_TRACE`, `LAP_LOG`, `CAR_DUMP`, `DT_PROBE`, `CARD_TRACE`…).

"Modo debug" no lançador liga esse pacote de uma vez:

| Debug | Off (padrão) | On |
|---|---|---|
| Barra superior (Settings/Mods/Debug/Help) | escondida (tela limpa) | visível, com os painéis |
| HUD de corrida (canto da tela) | — | fps do host, cadência, `delta`, relógio, mph, marcha, rpm, volta/segmento |
| Log de voltas (`RUMBLE_LAP_LOG`) | — | ligado (`~/Library/Logs/NascarRumbleNative.log`) |

### Opções

| Item | Valores | Efeito |
|---|---|---|
| Start Game | — | inicia o boot com as opções escolhidas |
| Frame Rate | `30` (padrão) / `60` | ritmo da corrida (`NativeHooks.RaceFrameMs`); 60 marcado como experimental |
| Show FPS | `Off` (padrão) / `On` | contador de quadros do jogo no canto superior direito da imagem 4:3 |
| Debug Mode | `Off` / `On` | tabela acima |
| Quit | — | fecha |

As escolhas ficam salvas em `launcher.json` (ao lado do `settings.json`, ignorado pelo Git).
Controles: os mesmos do jogo (teclado mapeado e gamepad, via `Controller.State`): ↑↓ seleciona,
←→ muda, ✕/Start confirma. Automação: `RUMBLE_LAUNCHER=0` pula o lançador (os roteiros de medição
continuam funcionando); variáveis `RUMBLE_*` explícitas continuam valendo e têm prioridade.

## Implementação

1. **RecompOne (patch genérico, pequeno):** `Runtime.PreBoot` (callback após validar o disco),
   `Runtime.PumpUi()` (processa janela/entrada/render sem o jogo), `Runtime.UiOverlay` (callback
   ImGui desenhado por cima de tudo), `Runtime.CreateUiTexture(rgba,w,h)`, `Runtime.UiFonts`
   (fontes extras carregadas na criação do ImGui) e `Runtime.SetTopBarVisible(bool)`.
2. **Host:** `LscImage` (decodificador BS v2), `Launcher` (estado, entrada, desenho no estilo do
   jogo, preferências), `DebugHud` (overlay da corrida), `NativeHooks` com ritmo configurável.
3. **Validação:** decodificador contra `jpsxdec`; lançador por captura de tela da janela; boot a
   30 e 60 fps; debug On/Off; `RUMBLE_LAUNCHER=0`; `make native-build`, testes, `git diff --check`,
   patch canônico regenerado e verificado (`git archive` + `apply` + `diff -r`).

## Depois (V2)

- Decodificar a fonte `Cfnt` do jogo e usá-la no lançador (fidelidade total do texto).
- Usar o mesmo estilo num **menu de pausa do host** (tecla dedicada) para trocar 30/60 e debug sem
  reiniciar.
- Itens extras úteis para teste: pular intro, ir direto para corrida (pista/carro/oponente), gravar
  e reproduzir uma volta (teste de regressão determinístico).

## Status (2026-10-08)

V1 implementada e validada:

- `recompone/host/LscImage.cs`: decodificador BS v2. Contra o `jpsxdec` no `FELD.LSC`: diferença
  média de 1,5 nível por canal (as maiores diferenças ficam nas bordas de cor, porque o `jpsxdec`
  interpola o croma). Diagnóstico: `NascarRumbleNative --decode-lsc <cue> CW/FEND/FELD.LSC out.ppm`.
- `recompone/host/Launcher.cs`: tela com Start Game / Frame Rate / Debug Mode / Quit no estilo do
  menu do jogo; navegação pelo mesmo mapeamento do jogo; `launcher.json` salvo no diretório de
  trabalho (ignorado pelo Git). ↑ a partir de Start Game dá a volta até Quit, como uma lista circular.
- `recompone/host/DebugHud.cs`: HUD com fps do host, limite da corrida, relógio, `delta`, mph,
  marcha, rpm (>>8), volta, segmento e aderência; conferido contra o velocímetro do jogo.
- Patch do RecompOne: `Runtime.PreBoot`, `PumpUi`, `UiOverlay`, `UiFontRequests/UiFonts`,
  `CreateUiTexture`, `TopBarOverride`, `WindowPixelSize`.
- Fonte: Arial Narrow Bold (sistema macOS); a fonte original (`Cfnt`) fica para a V2.

## Show FPS (2026-10-08)

Item novo no lançador (`launcher.json` → `ShowFps`; também `RUMBLE_SHOW_FPS=1`). Desenhado por
`recompone/host/HostOverlay.cs` no canto superior direito da imagem 4:3 do jogo, no estilo das
caixas de dica (borda lilás), com ponto verde (≥50), amarelo (≥25) ou vermelho.

O que é contado é **quadro do jogo**, não quadro do host: na corrida, uma iteração do laço de
corrida (`FUN_800269c0`, gancho `RaceTimingEnter`); fora dela, cada troca de buffer pedida pelo
jogo (`FUN_8001a24c`, gancho `FrameSubmitted`). Na corrida `FUN_8001a24c` é chamada várias vezes
por quadro (uma por lista de desenho), por isso não serve de contador ali — dava ~200 "fps".
Conferido: menus a 60, corrida a 30 com `Frame Rate 30`. Com debug ligado, o HUD de debug desce
para não sobrepor o contador e mostra `Game N fps` ao lado do fps do host.

## Atalho de teste: RUMBLE_QUICK_FINISH=1

Para validar campeonato/resultados sem pilotar todas as voltas: 5 s após a largada o host põe o
carro humano na última volta (`+0x328 = voltas - 1`, voltas em `*(0x800AF744)+0x14`) com o
acumulador de distância da volta (`+0x324`) cheio; a checagem original de volta (`FUN_8003014c`)
fecha a prova assim que o carro anda para frente (segurar ✕ uns segundos). Trocar `+0x22` do
jogador de `0x01` para `0x11` **não** faz a IA pilotar (o carro fica parado) — a IA precisa de
estado próprio criado no spawn. Os tempos do jogador ficam irreais e entram nos recordes da sessão.
