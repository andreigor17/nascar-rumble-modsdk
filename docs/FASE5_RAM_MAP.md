# Fase 5 — Mapa de RAM (RAM_MAP.md) via PCSX-Redux

> Objetivo: localizar as **estruturas vivas** do jogo na memória (posição/velocidade do carro,
> volta, timer, carro carregado, IA/power-ups) por *memory diffing*, e registrar em `docs/RAM_MAP.md`.
> Isso destrava a pesquisa de gameplay (Fase 8), o Memory Inspector e o mapeamento roster→livery.

## Por que PCSX-Redux (e não DuckStation)

O PCSX-Redux tem **Lua scripting** e um **Web Server (API HTTP)** que permite **ler/escrever a
memória do jogo por fora**. Ou seja: você joga, e eu leio a RAM e faço o diffing do meu lado.
Além disso traz o **OpenBIOS** embutido — roda o jogo **sem precisar de BIOS real**.

## Passo 1 — Instalar e rodar (você)

1. Baixe o PCSX-Redux para macOS (Apple Silicon) no site oficial:
   **https://pcsx-redux.consoledev.net/** → seção *Getting Started / Install* → build de macOS.
   (Descompacte e arraste `PCSX-Redux.app` para `/Applications`. Se o Gatekeeper reclamar:
   `xattr -dr com.apple.quarantine /Applications/PCSX-Redux.app`.)
2. Abra o PCSX-Redux. Se pedir BIOS, escolha usar o **OpenBIOS** (Configuration → BIOS).
3. Carregue o jogo: **File → Open ISO** (ou *Open Disk Image*) apontando para
   `NASCAR Rumble (USA)/NASCAR Rumble (USA).cue`. O jogo deve iniciar.

## Passo 2 — Ligar o Web Server (para eu ler a memória)

- Menu **Configuration → Emulation** (ou *Settings*): habilite **"Enable Web Server"**.
  Porta padrão **8080**. (Se houver campo de porta, deixe 8080.)
- Confirme que ficou ativo: com o jogo aberto, eu testo `http://localhost:8080/` do meu lado.

> Alternativa (se o Web Server não expuser leitura de memória na sua versão): uso a **console Lua**
> (menu *Debug → Lua console*) com um script que eu forneço para despejar a RAM num arquivo — e eu
> leio o arquivo. Decidimos qual caminho após ver a sua versão.

## Passo 3 — Memory diffing (juntos)

Técnica clássica de "cheat search":
1. Escolhemos um valor observável (ex.: **contador de voltas**, **velocidade**, **timer**).
2. Você deixa o jogo num estado A; eu tiro um retrato da RAM.
3. Você muda o valor (dá uma volta, acelera); eu tiro o retrato B.
4. Eu **diffo** A×B e vou estreitando até 1 endereço. Repetimos para cada variável.
5. Cada endereço confirmado entra em `docs/RAM_MAP.md` com evidência.

Alvos iniciais (ordem sugerida):
- Contador de voltas e posição na corrida (fáceis, mudam em passos discretos).
- Velocidade e posição (X,Y,Z) do carro do jogador.
- A partir da struct do jogador, achar o **array de carros da IA** (mesmo layout, offsets seguidos).
- Índice do carro carregado (fecha o mapeamento **roster→livery** que ficou pendente).

## Entregável

`docs/RAM_MAP.md` com os endereços confirmados (nome, endereço, tipo, evidência, classificação
✅🟡🔵). Base do **Memory Inspector** e do futuro **Save Editor**.

## Setup concluído (2026-07-22) — ✅

- PCSX-Redux instalado em `/Applications` (build ARM oficial do distrib.app); **OpenBIOS** ativo
  (sem BIOS real). Config em `~/.config/pcsx-redux/pcsx.json` com `emulator.Debug.WebServer=true`.
- Jogo carregado via `open -a PCSX-Redux --args -iso "<.cue>" -run`.
- **Web API confirmada:** `GET http://localhost:8080/api/v1/cpu/ram/raw` → 2 MB de RAM (offset 0 =
  `0x80000000`). Verificado: roster em `0x800aa700` bate com a análise estática (John Andretti #43).
  Também: `/api/v1/gpu/vram/raw` (VRAM) e `/api/v1/execution-flow` (status/controle).
- Ferramenta: **`scripts/memsearch.py`** (cheat-search com numpy). Comandos: `new u8|u16|u32`,
  `snap`, `eq <v>`, `changed`, `unchanged`, `inc`, `dec`, `list`.

## Controle autônomo total (2026-07-22) — ✅ olhos + mãos + memória

O Claude controla o jogo **sozinho**, sem depender do usuário observar/jogar:

- **Canal Lua arbitrário:** lançar o emulador com `-dofile scripts/pcsx_bootstrap.lua` registra o
  handler `POST /api/v1/lua/x?code=<lua>` (executa Lua qualquer: memória, GPU, input, execução).
  Comando de launch:
  ```bash
  open -a PCSX-Redux --args -iso "<.cue>" -run -dofile "<repo>/scripts/pcsx_bootstrap.lua"
  ```
- **Ver a tela:** `GET /api/v1/gpu/vram/raw` (VRAM 1024×512, 16bpp X1B5G5R5) → screenshot dos 2
  framebuffers. Dá pra ler HUD (velocidade, volta, posição, piloto).
- **Input do controle:** `pad.setOverride(bit)` segura, `pad.clearOverride(bit)` solta (⚠️ PONTO, não `:` — a função espera o botão como 1º arg)
  (`PCSX.SIO0.slots[1].pads[1]`). Bits: SELECT=0 START=3 UP=4 RIGHT=5 DOWN=6 LEFT=7 L2=8 R2=9
  L1=10 R1=11 TRIANGLE=12 CIRCLE=13 CROSS=14 SQUARE=15. (Ativo-baixo: override zera o bit = pressiona.)
- **Memória:** `GET/POST /api/v1/cpu/ram/raw` (POST precisa `?offset=&size=` + corpo de `size` bytes).
- **Ferramenta:** `scripts/pcsx.py` (lua/tap/press/release/rd/wr/shot) + `scripts/memsearch.py`.

> Com isso o Claude navega menus, entra em corrida, dirige e faz o diffing por conta própria.

### Metodologia de teste controlado (evita contaminação por batida)

⚠️ Dirigir só em linha reta faz o carro **bater/sair da pista** em certos trechos, impedindo
atingir a velocidade real (numa reta limpa o carro chega a ~181; batendo, parava em ~113).
Solução:
- **Esterçar:** `LEFT`(7)/`RIGHT`(5) mantêm o carro na pista.
- **Savestate como ponto de restauração:** `PCSX.createSaveState()` (guardar num global Lua
  `_RESTORE` — **nunca** imprimir o objeto, tem ~20 MB) e `PCSX.loadSaveState(_RESTORE)` para
  resetar ao mesmo ponto limpo a cada teste. Round-trip confirmado (volta à posição/velocidade exatas).
- Fluxo: posicionar numa reta → `save_state` → aplicar input controlado → `pause` → ler RAM →
  `load_state` para repetir de forma idêntica. Comandos em `scripts/pcsx.py`.
- Controles: **CROSS**=acelerar, **SQUARE**=frear/ré, **LEFT/RIGHT**=esterçar.

## Como caçamos uma variável (ex.: contador de voltas)

```
python scripts/memsearch.py new u8      # estado A (candidatos = todos)
python scripts/memsearch.py eq 1        # onde valor == volta atual
# (jogador completa uma volta)
python scripts/memsearch.py snap
python scripts/memsearch.py eq 2        # estreita para os que viraram 2
# repetir até sobrar 1 endereço -> registrar no RAM_MAP.md
```

**Próximo passo (você):** entrar numa corrida no jogo. Aí eu diffo ao vivo — começando pelo
contador de voltas — e vou preenchendo o `docs/RAM_MAP.md`.
