# Sessão 011 (2026-10-08) — Intro/menu concluídos e investigação da física da corrida

> **Leia primeiro na próxima sessão.** Este arquivo registra o estado exato do port nativo, as
> alterações ainda não commitadas, os testes visuais feitos com o usuário e o próximo ponto de
> investigação.
>
> **Atualização no fim do dia:** a flutuação foi resolvida (bug do comando GTE `OP` no RecompOne) e o
> desempenho da corrida melhorou (~12 → ~33 quadros/s, relógio em tempo real). Leia as seções
> **"Continuação"** e **"Continuação 2"** no fim deste arquivo antes de qualquer outra coisa; as
> hipóteses e próximos passos da primeira metade estão superados.

## Resumo executivo

- O host nativo macOS ARM agora reproduz a intro inteira, atravessa o carregamento, chega ao menu
  principal e aceita input.
- A intro pode ser pulada como no PS1: o teste com **Z/Cross** foi bem-sucedido e levou da intro ao
  carregamento/menu. A intro não foi removida.
- O modo demo ocioso do menu abre uma pista e os veículos avançam pelo circuito.
- Uma corrida iniciada manualmente pelo usuário também abre e contém seis veículos.
- Foi corrigida uma falha real de cadência: a simulação recebia `delta=25` porque cada submissão de
  lista gráfica produzia um VBlank. Agora o delta converge para e permanece em `5`, igual ao avanço
  de cinco unidades feito pelo callback de VBlank original.
- Apesar da correção de tempo, a física continua incorreta. Os carros aparecem em alturas muito
  diferentes na mesma largada, levitam, quicam e às vezes são arremessados para o céu.
- O indício principal passou a ser a consulta de altura/colisão do terreno em
  `FUN_80065488 -> FUN_80064acc`, e não o relógio, o modo demo ou o X/Z inicial do grid.
- O último processo nativo foi encerrado com `Ctrl-C`; a verificação final confirmou que não havia
  jogo nem PCSX-Redux rodando.
- Nenhum commit foi solicitado ou criado. O worktree contém alterações importantes em andamento.

## Estado funcional observado

### Funciona

1. Janela OpenGL 4.1 no macOS ARM.
2. Inicialização de heap, BIOS/SDK, memory card, controle, GPU, SPU e CD.
3. Tela legal, logos e intro `CW/OPENING/INTRO.WVE` completa.
4. Áudio/streaming da intro deixa de travar no antigo underflow após o bombeamento cooperativo de
   IRQs da SPU e DMA.
5. Carregamento que existe entre a intro e o menu, inclusive a barra de progresso.
6. Menu principal completo.
7. Input real no host; Z atua como Cross e pula a intro.
8. Transição ociosa do menu para `Rumble Demo`.
9. Entrada em corrida demo e corrida manual, com mapa, HUD, veículos e atualização da simulação.
10. Fechamento controlado das sessões de diagnóstico pelo terminal, sem processo órfão conhecido.

### Ainda não funciona corretamente

1. Altura/contato dos veículos com o terreno.
2. Física e IA utilizáveis: os carros levitam, sobem/descem, voam ou entram em ciclo de reset.
3. Uma corrida completa do início ao fim ainda não foi validada.
4. Áudio, HUD, power-ups, voltas, resultado, retorno ao frontend e saves ainda não passaram pelo
   gate de uma corrida completa.
5. A Etapa 5 chegou funcionalmente ao menu/input, mas ainda não foi marcada concluída porque a
   validação formal final do gate e o fechamento normal pelo próprio aplicativo estão pendentes.

## Alterações existentes no worktree

Arquivos modificados, todos ainda sem commit:

- `recompone/host/NativeHooks.cs`
- `recompone/nascar.json`
- `recompone/nascar_funcmap.json`
- `recompone/patches/recompone-macos.patch`
- `tests/test_native.py`
- documentação atualizada nesta sessão

### Patch local do RecompOne

`recompone/patches/recompone-macos.patch` preserva todas as adaptações necessárias ao runtime:

- passagem direta do caminho do CUE e ocultação do seletor quando ele é válido;
- carregador de mods desligado por padrão, ativável somente por `RUMBLE_ENABLE_MODS=1`;
- fallbacks de OpenGL 4.1 para macOS, inclusive barreira e cópia de VRAM por framebuffer;
- correções e entrega cooperativa de eventos de memory card;
- IRQ de DMA diferida para impedir callbacks/reentrância no meio da escrita do CHCR;
- manutenção correta do FIFO/consumo e callbacks do CD;
- registro e entrega de IRQ da SPU;
- `Runtime.PresentFrame()`, `PumpCd()` e `PumpSpu()` entregando os eventos assíncronos no thread do
  host.

Se o runtime do RecompOne for recriado ou atualizado, reaplicar esse patch pelo fluxo de
`scripts/build_native.py`; não editar apenas a cópia gerada dentro de `tools/RecompOne`.

### Funcmap e callbacks indiretos

O `recompone/nascar_funcmap.json` recebeu entradas que antes eram alcançadas apenas por ponteiros e
precisam existir no dispatcher recompilado. Entre elas:

- áudio/SPU: `0x80020160`, `0x80020658`, `0x80021f9c`, `0x800221f8`, `0x800224f4`,
  `0x80022e40`, `0x80023b34`;
- carregamento do frontend: `0x80029f7c`;
- callbacks de objetos: `0x80030f84`, `0x8003203c`, `0x80033274`, `0x80033468`,
  `0x80034198`, `0x800343dc`, `0x80034894`, `0x80034e6c`, `0x80060190`;
- callbacks de entidades: `0x8003be84`, `0x800481bc`, `0x8006a214`, `0x8006e074`,
  `0x8006fa04`, `0x80074fd0`.

Essas inclusões eliminaram falhas de dispatch durante intro, carregamento, frontend e demo.

### Hooks atualmente configurados

`recompone/nascar.json` possui **11 patches**:

| Função original | Modo | Hook/alvo | Motivo |
|---|---:|---|---|
| `FUN_8001f560` | post | `MemoryCardPoll` | ceder ao scheduler/eventos durante polling |
| `CD_sync` | replace | `LibCd.CdSync` | sincronização de CD do runtime |
| `CD_ready` | replace | `CdReady` | estado de leitura esperado pelo jogo |
| `FUN_8001a24c` | post | `FrameSubmitted` | apresentar quadro e controlar cadência de VBlank |
| `FUN_800285e4` | pre | `FrontendFrameWait` | bootstrap/cadência do frontend |
| `FUN_8007a994` | pre | `FrontendUpdateEnter` | guardar `S0/S1/S2/SP` |
| `FUN_8007a994` | post | `FrontendUpdateExit` | restaurar `S0/S1/S2/SP` |
| `FUN_800269c0` | pre | `RaceTimingEnter` | entrar no regime de tempo da corrida |
| `FUN_800269c0` | post | `RaceTimingTrace` | diagnóstico temporal sob trace |
| `FUN_80056c6c` | post | `VehicleStateTrace` | diagnóstico de posição/velocidade sob trace |
| `FUN_80096e90` | pre | `IntroAudioPoll` | entregar IRQs da SPU/DMA durante espera da intro |

Os rastreadores `RaceTimingTrace` e `VehicleStateTrace` são temporários, mas inertes quando
`RUMBLE_NATIVE_TRACE` não é `1`. Removê-los ou reduzi-los somente depois de resolver e validar a
física.

## Correções que destravaram intro, carregamento e menu

### Áudio da intro

O bloqueio anterior era interpretado como falta de novos setores de CD. A leitura do código mostrou
que `FUN_80096e90` aguardava espaço/liberação do ring buffer consumido pela SPU. O hook foi corrigido
para bombear `Runtime.PumpSpu()`, não `PumpCd()`. O runtime passou a registrar o endereço de IRQ da
SPU, sinalizar quando a transferência alcança esse endereço e entregar a IRQ 9 de forma cooperativa.
Isso permitiu que a intro prosseguisse até o fim.

### Carregamento/frontend

- `FrameSubmitted` passou a chamar `PresentFrame`, permitindo que DMA/VBlank/eventos continuassem
  enquanto o jogo desenha.
- `FrontendFrameWait` fornece o primeiro tick depois que o frontend zera seus contadores.
- O dispatcher grande `FUN_8007a994` corrompia no caminho recompilado o contexto salvo do chamador;
  `FrontendUpdateEnter/Exit` preserva explicitamente os registradores callee-saved `S0`, `S1`, `S2`
  e `SP` na fronteira.
- Os callbacks indiretos adicionais foram inseridos no funcmap, evitando alvos ausentes.

## Testes de input e atalho da intro

AppleScript/tecla global falhou por falta de permissão de Acessibilidade do macOS. O teste confiável
foi enviar `CGEvent` diretamente ao PID do processo .NET, o que não exigiu essa permissão:

```sh
pid=$(pgrep -n -f 'NascarRumbleNative.dll')
swift -e 'import CoreGraphics; import Foundation; let pid = pid_t(CommandLine.arguments[1])!; let down = CGEvent(keyboardEventSource: nil, virtualKey: 6, keyDown: true)!; let up = CGEvent(keyboardEventSource: nil, virtualKey: 6, keyDown: false)!; down.postToPid(pid); usleep(150000); up.postToPid(pid)' "$pid"
```

- keycode macOS `6` = Z = Cross no mapeamento testado;
- keycode `36` = Enter/Start;
- setas direcionais também responderam;
- Z durante a intro pulou para o carregamento e depois para o menu;
- isso apenas testa o skip original: a intro permanece no jogo e continua reproduzível.

## Comparação com a referência

A mesma imagem legal foi executada no PCSX-Redux:

```sh
'/Applications/PCSX-Redux.app/Contents/MacOS/PCSX-Redux' \
  -iso '/opt/Projetos/rumble/NASCAR Rumble (USA)/NASCAR Rumble (USA).cue' \
  -run
```

Na referência, a corrida demo inicia e os carros permanecem corretamente apoiados na pista. Isso
confirma que o comportamento aéreo é defeito do port/runtime, não uma característica da demo ou dos
dados da imagem. Evitar `-stdout` no PCSX-Redux, pois ele gerou volume excessivo de logs.

Referência dos argumentos do emulador: <https://pcsx-redux.consoledev.net/cli_flags/>.

## Diagnóstico da cadência da corrida

O primeiro `RaceTimingTrace` revelou, após 60 atualizações lógicas:

```text
raw ~= 2065
delta = 25 (limite de segurança da simulação)
```

O callback original `vblank_tick_callback` em `0x8001dcd4` soma **5** ao relógio por VBlank. A
causa era `FrameSubmitted` chamar `PresentFrame()` para toda chamada de `FUN_8001a24c`; uma corrida
submete várias listas gráficas dentro da mesma atualização lógica e, portanto, recebia cerca de sete
VBlanks/35 unidades por frame até bater no limite 25.

Uma primeira tentativa de condicionar `FrameSubmitted` globalmente corrigiu a corrida, mas atrasou
ou impediu o lançamento esperado da demo ociosa porque alterou a cadência do frontend. A solução
atual separa os regimes:

- `_raceTimingActive=false` no frontend, preservando seu avanço anterior;
- `RaceTimingEnter` ativa o regime da corrida e garante um VBlank pendente antes do busy-wait;
- durante a corrida, `FrameSubmitted` só avança o runtime quando o tick anterior já foi consumido.

Resultado medido depois da correção:

```text
delta inicial: 8, 7, 6, 6
delta estável: 5, 5, 5, ...
raw: avanço de 5 por atualização lógica
```

O mapa de globals confirmado com `GP = 0x800af0e4` é:

| Expressão | Endereço | Significado observado |
|---|---:|---|
| `GP+0x654` | `0x800af738` | relógio bruto de VBlank |
| `GP+0x634` | `0x800af718` | relógio consumido |
| `GP+0x664` | `0x800af748` | snapshot/tempo da corrida |
| `GP+0x5fc` | `0x800af6e0` | delta da simulação |
| `GP+0x600` | `0x800af6e4` | estado da corrida |
| `GP+0x604` | `0x800af6e8` | quantidade de jogadores locais |
| `GP+0x6e8` | `0x800af7cc` | quantidade de veículos |
| absoluto | `0x800b12c0` | tabela de ponteiros de veículos |

Conclusão: o excesso de tempo era um bug verdadeiro e foi corrigido, mas não era a única causa da
física incorreta.

## Teste atual: corrida manual e estado dos veículos

O usuário entrou manualmente em uma corrida enquanto `RUMBLE_NATIVE_TRACE=1` estava ativo. O trace
mostrou `state=4`, `localPlayers=1` e `vehicles=6`, eliminando a hipótese de que o problema existia
somente no modo demo.

Na primeira atualização, as posições foram:

```text
0=(444184,21562,1001695)
1=(456178,41631,1000946)
2=(449893,42061,996706)
3=(437899,45055,997456)
4=(432190,35910,1002445)
5=(425904,45377,998205)
```

Na segunda atualização, a ordem/tabela já aparecia assim:

```text
0=(425904,45377,998205)
1=(432184,40114,1002421)
2=(437925,45378,997472)
3=(444184,21562,1001695)
4=(449896,43791,996647)
5=(456166,43430,1000263)
```

Conclusões objetivas:

- X e Z formam seis posições distintas e plausíveis de grid; a hipótese de todos nascerem no mesmo
  ponto foi **descartada**.
- Y varia de `21562` a `45377` em carros da mesma área de largada, diferença grande demais e
  compatível com uma altura de terreno incorreta.
- A captura manual mostrou o carro do jogador parado em `N/000`, suspenso acima da estrada do
  cânion, e outro carro muito alto no céu.
- Mais tarde, o carro monitorado entrou em padrão de reset/oscilação: em torno do frame 840 estava
  em `(393386,55797,1011074)` e depois alternava próximo de `(393216,55808,1002496)` e
  `(393388,55787,1011137)`. As velocidades ficavam pequenas/reiniciadas, sugerindo que a lógica de
  recuperação é acionada após uma altura/colisão inválida.

## Hipótese principal e caminho de código

Em `FUN_8003132c` (criação do grid), o jogo calcula X/Z e então chama:

```c
local_5c = FUN_80065488(&local_70, &local_60, 0);
```

`local_60` contém X, `local_58` contém Z e o retorno `local_5c` é usado como Y/altura do terreno.
`FUN_80065488` coloca temporariamente `Y=-1`, chama
`FUN_80064acc(param1, param2, 0, 1)` e restaura o Y anterior. Portanto, o próximo alvo é a consulta
de terreno/interseção em `FUN_80064acc` e seus auxiliares:

- `FUN_800647f4`
- `FUN_80064998`
- `FUN_800650b0`
- `FUN_80065194`
- `FUN_80065844`

`FUN_80064acc` tem aproximadamente 1508 bytes, é amplamente usada por colisão/altura e chama testes
de triângulo que usam GTE `OP`. A função principal de simulação veicular `FUN_80056c6c` tem cerca de
10768 bytes; o hook atual roda depois dela apenas para observar estado.

### GTE já verificada, sem correção especulativa

Foram comparadas as implementações de `OP` e das variantes de `MVMVA` usadas pelo jogo em
`tools/RecompOne/RecompOne.Runtime/Hardware/Gte.cs` com o código atual do PCSX-Redux:

- <https://github.com/grumpycoders/pcsx-redux/blob/main/src/core/gte-instructions.cc>
- <https://github.com/grumpycoders/pcsx-redux/blob/main/src/core/gte-internal.h>

As fórmulas relevantes parecem estruturalmente corretas. O jogo não usa nesses caminhos as variantes
problemáticas de `MVMVA` com matriz `mx=3` nem a combinação especial `cv=2`. Existem diferenças
potenciais de fidelidade — overflow de 44 bits por soma e leitura assinada de alguns controles —,
mas não há evidência de que expliquem este defeito. **Não fazer uma mudança ampla na GTE sem um
trace que prove divergência.**

## Capturas locais da investigação

Esses arquivos estão em `/tmp` e podem desaparecer após reboot/limpeza:

- `/tmp/rumble-menu-check.png` — menu completo;
- `/tmp/rumble-skip-test.png` — caminho após pular intro;
- `/tmp/pcsx-skip.png` — referência no PCSX-Redux;
- `/tmp/rumble-timing-state.png` — demo antes da correção temporal;
- `/tmp/rumble-race-delta5.png` e `/tmp/rumble-race-delta5-later.png` — corrida com delta 5;
- `/tmp/rumble-race-fixed-motion.png` — movimento após correção de cadência;
- `/tmp/rumble-manual-window.png` — melhor evidência da corrida manual: carro sobre a pista e
  adversário no céu;
- `/tmp/rumble-demo-float.png`, `/tmp/rumble-trace-demo.png` e
  `/tmp/native-after-demo-input.png` — sintomas anteriores da física.

## Build e validação conhecidos

Ferramenta correta:

```text
/Users/andre/.dotnet/dotnet 10.0.302
```

Não usar o `dotnet` de sistema 8 para esta trilha. O último `make native-build`, já com os 11
patches, terminou com sucesso:

```text
2004 funções recompiladas
58 jump tables / 979 entradas
11 patches
22 reimplementações
53 avisos conhecidos de caminhos inalcançáveis
0 erros
```

Ao encerrar esta sessão, `python3 -m unittest tests.test_native -v` passou com os **5 testes** no
worktree atual e `git diff --check` também passou. Isso valida estrutura/configuração, não a física;
o `make native-build` acima continua sendo o último build completo conhecido com os 11 patches.

## Como reproduzir rapidamente

```sh
cd /opt/Projetos/rumble
/Users/andre/.dotnet/dotnet --version
make native-build
RUMBLE_NATIVE_TRACE=1 make native-run
```

Para chegar rápido ao menu, enviar Z/Cross ao PID com o comando de `CGEvent` acima. Deixar o menu
ocioso inicia a demo; alternativamente, navegar e iniciar uma corrida manual para confirmar
`localPlayers=1`.

## Próximos passos exatos

1. Instrumentar `FUN_80065488` e/ou `FUN_80064acc` sem alterar sua lógica, registrando para cada um
   dos seis carros de largada: X/Z consultados, Y anterior, altura retornada, setor/triângulo
   selecionado e qualquer sentinela de falha.
2. Obter os mesmos valores na execução de referência do PCSX-Redux para a mesma pista/coordenadas,
   por debugger, Lua ou leitura de RAM, e localizar a primeira divergência — entrada, seleção de
   setor/triângulo ou resultado matemático.
3. Auditar `FUN_80064acc` e auxiliares com foco em:
   - sinais de entradas/saídas e comparações signed/unsigned;
   - empacotamento/alinhamento de coordenadas e índices;
   - entradas e saídas GTE `OP`, especialmente `MAC1/MAC2`;
   - fronteiras de função e jump tables do RecompOne;
   - integridade de stack e registradores callee-saved em callbacks/chamadas indiretas.
4. Só modificar a GTE ou a física depois de localizar uma divergência reproduzível.
5. Após a correção, repetir nesta ordem: intro normal, skip com Z, carregamento, menu, demo ociosa,
   corrida manual. Confirmar `delta=5`, seis carros no chão, aceleração, direção e IA.
6. Quando a física estiver estável, remover/reduzir os traces temporários e executar:

```sh
python3 -m unittest tests.test_native -v
make native-build
make ci-public
git diff --check
cd tools/RecompOne
git apply --unidiff-zero --reverse --check ../../recompone/patches/recompone-macos.patch
```

7. Se houver mudança no runtime em `tools/RecompOne`, atualizar também o patch canônico
   `recompone/patches/recompone-macos.patch`; caso contrário a correção desaparecerá no rebuild.
8. Não publicar/commitar até o mantenedor pedir. Nenhum BIN, CUE, EXE ou asset proprietário deve
   entrar no Git.

## O que não repetir

- Não voltar a tratar o problema como underflow de CD da intro; essa etapa foi atravessada.
- Não assumir que a demo parada é falta de countdown: depois do ajuste temporal os carros avançam.
- Não culpar o modo demo: a corrida manual apresenta o mesmo defeito.
- Não investigar sobreposição X/Z do grid: os seis X/Z são distintos.
- Não restaurar `PresentFrame()` incondicional dentro da corrida: isso volta a produzir muitos
  VBlanks e `delta=25`.
- Não aplicar correções especulativas amplas à GTE antes de comparar entradas/saídas com a referência.

---

## Continuação (2026-10-08, tarde) — causa raiz da física: bug no OP da GTE

> **Resolvido o defeito de altura/colisão.** Os carros flutuavam porque o comando GTE `OP`
> (cop2 `0x0C`, produto vetorial) do RecompOne calculava MAC2/MAC3 com IR1/IR2 já sobrescritos
> pelo resultado anterior. Corrigido em `tools/RecompOne/.../Hardware/Gte.cs` e acrescentado ao
> patch canônico `recompone/patches/recompone-macos.patch`.

### Método: verificação diferencial (shadow)

Novo `recompone/host/ShadowCpu.cs` (ativado só com `RUMBLE_SHADOW=1`): antes de cada chamada
recompilada, um interpretador R3000 executa o **código MIPS original** (o EXE fica carregado em
`0x80010000` na RAM emulada) sobre o mesmo estado de CPU/GTE/RAM, com escritas num overlay e GTE
salva/restaurada; após o retorno, compara V0 e as escritas com o C# gerado. Hooks pre/post em
`FUN_80064acc`, `FUN_80065488` e `FUN_80056c6c` (o post desta última vai por `VehicleStateTrace`).

### Sequência de evidências

1. Trace de `FUN_80065488` (chamado por `FUN_8004c368`, que pré-calcula a altura de cada ponto da
   linha de corrida) mostrava alturas consecutivas absurdas: `10892, 13644, 49601, 6413, 28422…`.
2. Shadow com a GTE do runtime: **0 divergências** em >60.000 chamadas de `FUN_80064acc` e em todos
   os quadros de `FUN_80056c6c`, com e sem load-delay. ⇒ a tradução MIPS→C# dessas funções está correta.
3. Dump da RAM nativa (`RUMBLE_RAM_DUMP=<arquivo>`, gravado no 1º quadro da corrida) comparado com
   `CW/LOCMC/MC2.TRK` extraído do disco: as 116 `TSEG`, `TCOL` e `TIGR` batem byte a byte depois de
   aplicar as relocações do parser `FUN_80062088`. ⇒ os dados de colisão estão corretos.
4. Porta Python independente da consulta (`FUN_80064acc` + `FUN_800647f4` + `FUN_80064998`, OP com
   inteiros de 16 bits exatos) sobre o dump: alturas suaves `30429, 28980, 27405, 26251, 25106` nos
   **mesmos** setores/triângulos escolhidos pelo nativo. Grid de largada ≈ 8066–8274 em todos os carros.
5. Variante do shadow com GTE mínima independente reproduziu `0x76dd = 30429` contra `0x2a8c = 10892`
   do runtime. O cross-check registrou, por exemplo:
   `R11=0 R22=-92 R33=-80 IR1=32767 IR2=-396 IR3=-144` → esperado `MAC2=-2621360`,
   runtime `1474560 = -80 × (-18432)`, isto é, IR1 já substituído por MAC1. MAC1 sempre batia.

### Correção

```csharp
case 0x0C:
{
    long ir1 = IR1, ir2 = IR2, ir3 = IR3;   // operandos antes do comando
    SetMac(1, (long)RT[4] * ir3 - (long)RT[8] * ir2, sf, lm);
    SetMac(2, (long)RT[8] * ir1 - (long)RT[0] * ir3, sf, lm);
    SetMac(3, (long)RT[0] * ir2 - (long)RT[4] * ir1, sf, lm);
    break;
}
```

Os demais comandos (SQR, GPF, GPL, MVMVA, NCx, DPCx/INTPL) usam cada IR antes de sobrescrevê-lo ou
recebem os valores por cópia; só o OP tinha o aliasing.

### Resultado medido após a correção (demo MC2)

- Alturas da linha de corrida idênticas à porta Python.
- Grid: seis carros com `Y` entre 8700 e 8909 (duas filas), contra 8004–15613 antes.
- Carro monitorado acelera até ~40000 de velocidade e percorre a pista com `Y` entre 8415 e 8769
  por 1080 quadros, sem reset. `delta=5` preservado.
- Shadow: 0 divergências nas três variantes.
- `python3 -m unittest tests.test_native` → 7 testes OK (2 novos: patch da GTE e shadow opt-in).

### Observações

- A demo do PCSX-Redux sorteia a pista (veio LOCBB); a do nativo cai sempre em MC2 porque o RNG
  roda determinístico. Para comparar RAM com a referência, usar uma corrida manual na mesma pista.
- Para chegar à demo no nativo: apertar Z **uma única vez** durante a intro e não tocar mais em nada;
  um segundo Z no menu entra numa tela que não dispara a demo.
- A Web API do PCSX-Redux só aceita `GET /api/v1/cpu/ram/raw` completo (sem `offset/size` no GET).

### Próximos passos

1. Validação visual com o mantenedor: demo e corrida manual com carros no chão, colisão entre carros,
   curvas, IA.
2. Corrida completa (voltas, resultado, retorno ao frontend, áudio, power-ups, saves).
3. Manter o shadow como ferramenta: estender a funções suspeitas sempre que surgir comportamento
   estranho, antes de mexer em lógica.
4. Remover/reduzir os traces temporários quando o gate da corrida completa passar.

## Continuação 2 (2026-10-08, noite) — validação visual, desempenho e patch reproduzível

**Validação do mantenedor:** com a correção da GTE, os carros estão no chão na demo (confirmado
visualmente). A queixa seguinte foi FPS baixo na demo em relação ao PS1/PCSX-Redux, o que impedia
avaliar a IA.

### Diagnóstico do FPS

- A sessão observada pelo mantenedor rodava com `RUMBLE_SHADOW=1`, que interpreta a física inteira
  três vezes por quadro. **Nunca avaliar desempenho ou jogabilidade com o shadow ligado.**
- Mesmo sem shadow: ~12 quadros lógicos/s na corrida, com CPU do processo em ~29%. O `sample` do
  macOS mostrou ~90% da thread principal em `glFinish`.
- Origem: `GlVram.Barrier()` usava `glFinish()` no macOS (OpenGL 4.1 não tem `glTextureBarrier`), e
  `GlBackend.Flush()` chamava a barreira em **todo** lote de primitivas.
- Referência PCSX-Redux medida pela Web API: relógio `0x800af738` avança **300/s** (60 VBlanks × 5) e
  `delta` (`0x800af6e0`) fica em ~9–12, isto é, o jogo original desenha a ~25–30 quadros/s.
- No nativo cada quadro recebia exatamente um VBlank (`delta=5`); a 12 quadros/s a corrida andava a
  60/s, **5× mais lenta** que o tempo real.

### Correções

1. `RecompOne.Runtime/Gpu/Hle/Gl/GlBackend.cs`: barreira condicional. Rastreia o retângulo da VRAM
   escrito desde a última barreira (desenhos no FBO da VRAM, `Fill`, `WriteVram`, `CopyVram`,
   `Writeback`) e quais alvos de exibição foram escritos; o lote só sincroniza se ler textura/CLUT
   numa área suja ou se usar mask-check (`uDest`) num destino sujo. Resultado: ~33 quadros/s, CPU
   ~62%.
2. `recompone/host/NativeHooks.cs` (`DeliverElapsedVBlanks`): na corrida, depois do `PresentFrame`,
   entrega os VBlanks decorridos em tempo real (acumulador de 1/60 s, até 5 por quadro = teto
   `delta=25` do jogo). O relógio da corrida passou a ~277–300/s. Distribuição de `delta` em 700
   quadros: 5–25, mediana ~7. Carros continuam no chão (Y 8415–8794, velocidade ~40000).
3. `RUMBLE_NATIVE_TRACE=2` registra o `RaceTimingTrace` de todos os quadros (o modo 1 registra
   1 a cada 60).

### Patch canônico estava corrompido (corrigido)

O patch `recompone/patches/recompone-macos.patch` era gerado com `-U0` (sem contexto). Aplicado num
RecompOne limpo, vários blocos caíam em posições erradas: `BiosB.cs` ficava com `CardRead` mal
posicionado (não compilaria), `Dma.cs` notificava o setor de CD antes da leitura, além de
`HostWindow.cs`, `DiscPickerPopup.cs`, `PSMemory.cs` e `Runtime.cs` divergentes. A árvore local
funcionava só porque fora editada à mão. O patch foi **regenerado com `git diff` completo** e
verificado: `git archive` do commit fixado + `git apply` = árvore atual (`diff -r` vazio), e o
`--reverse --check` do build continua passando. Regra daqui em diante: regenerar sempre com contexto
e repetir essa verificação. `.gitattributes` isenta `*.patch` do `git diff --check` (as linhas de
contexto herdam espaços do upstream).

### Controles do teclado no nativo (`settings.json`, ignorado pelo Git)

| PS1 | Tecla | No jogo |
|---|---|---|
| Cross | Z | confirmar / acelerar |
| Square | A | frear / ré |
| Circle | X | voltar |
| Triangle | S | — |
| L1 / R1 | Q / W | — |
| L2 / R2 | E / R | — |
| Start | Enter | iniciar / pausar |
| Select | Shift direito | — |
| D-pad | setas | navegar / esterçar |

Para a demo: apertar Z **uma vez** durante a intro e não tocar mais em nada até a demo começar.

### Estado ao fim da sessão

- `make native-build`: 2004 funções, 58 jump tables / 979 entradas, 16 patches, 22 reimplementações.
- `python3 -m unittest tests.test_native`: 7 testes OK. `git diff --check`: OK.
- Pendências para a próxima sessão: o mantenedor vai avaliar a IA na demo e jogar uma corrida
  manual; depois disso, corrida completa (voltas, resultado, frontend), HUD, áudio, power-ups e
  saves. Se o FPS ainda incomodar, perfilar de novo com `sample <pid> 5` e atacar o próximo gargalo.

## Continuação 3 (2026-10-08) — travamento ao sair da corrida e 60 fps

### "Crash" ao confirmar Quit Race = loop infinito

Não era exceção: o processo ficava a 100% de CPU com a tela congelada em `Quit Race: NO/YES`.
`dotnet-stack report -p <pid>` (instalado em `~/.dotnet/tools`, rodar com `DOTNET_ROOT=~/.dotnet`)
apontou `FUN_800299a8` (laço da corrida). Ao sair do laço (estado `gp+0x600` ≠ 4/0xD), a função
envia um último quadro (`FUN_8001a24c(4)`) e gira em `L80029BB4` esperando o byte
`gp+0x63C` = `0x800AF720` zerar. Esse byte é o "swap pendente": `FUN_8001a24c` o liga e o callback
de VBlank `FUN_8001dac0` o desliga depois do `DrawSync`. Na corrida o VBlank vem do hook
`RaceTimingEnter`, que não é mais alcançado depois do Quit → nenhum VBlank, laço eterno.

Correção em `NativeHooks.FrameSubmitted`: com a corrida ativa e estado fora de {4, 0xD},
`FinishRaceTiming` desliga o modo corrida e entrega VBlanks até o flag zerar (guarda de 8).
Validado ao vivo: Quit volta ao menu principal, Restart reinicia, Continue retoma, e uma nova
corrida depois do Quit funciona. (Fim de corrida por bandeirada passa pelo mesmo caminho, mas
ainda não foi jogado até o fim.)

### Desempenho: `glBufferSubData` era ~62% da thread principal

`sample` na corrida mostrou `glBufferSubData` → `flushContext`/`semaphore_wait`: no OpenGL sobre
Metal da Apple, reescrever o VBO que o lote anterior ainda lê força um flush + espera **por lote**.
`GlBackend.Flush` agora re-especifica o buffer (`BufferData(..., StreamDraw)`, "orphaning").
Resultado: corrida de 32 → **60 fps** com CPU ~28% (patch canônico regenerado e verificado com
`git archive` + `apply` + `diff -r`).

Também corrigido `DeliverElapsedVBlanks`: o VBlank que o `PresentFrame` já entrega não era
descontado da dívida, então a 60 fps o relógio corria a 374 ticks/s. Agora fica em 300–301.

### 60 fps × dinâmica original

O motor é de passo variável (`delta` = 5 × VBlanks desde o último quadro, teto 25). A 60 fps o
jogo roda com `delta=5` fixo; o PS1 roda a ~25–30 fps (`delta` 9–12). Comparação no **Time Trial**
(Mark Martin #6 Rookie, Gold Rush, Z segurado, eixo = ticks do relógio do jogo após o GO;
`RUMBLE_NATIVE_TRACE=2` agora registra `mph=`):

| ticks | 60 fps | 30 fps (a) | 30 fps (b) |
|---|---|---|---|
| 400 | 93 | 75 | 74 |
| 600 | 106 | 96 | 94 |
| 800 | 119 | 110 | 109 |
| 1600 | 144 | 144 | 142 |
| 2000 | 153 | 155 | 153 |

0→100 mph: 495 ticks a 60 fps contra 660–665 a 30 fps; velocidade final igual (~160). As duas
rodadas a 60 fps foram idênticas (determinístico). Conclusão: parte da lógica avança **por
quadro** e não por `delta` (suspeita: troca de marcha/embreagem ou suavização do acelerador).
Por isso:

- **padrão = 30 fps** (cada quadro da corrida segura dois VBlanks, `delta=10`, como no console);
- `RUMBLE_RACE_FPS=60` liga os 60 fps (experimental). Outros valores entre 1 e 60 também valem.

### Próximos passos para os 60 fps "sem alterar a dinâmica"

1. Achar as variáveis por quadro na física (`FUN_80056c6c` e chamadas): rastrear marcha/rpm/
   acelerador por quadro a 30 e 60 fps e ver qual muda de ritmo. O shadow/trace já dá a base.
2. Para cada uma, escalar pelo `delta` num hook (ou rodar a lógica "por quadro" só a cada
   10 ticks acumulados), mantendo a renderização a 60.
3. Critério de aceite: curvas de mph×ticks a 60 iguais às de 30 (e às do PCSX-Redux), mais IA e
   tempos de volta equivalentes.
