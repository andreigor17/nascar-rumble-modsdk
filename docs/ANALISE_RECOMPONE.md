# Análise Rigorosa — RecompOne (recompilador estático de PS1)

> Repo: https://github.com/BlackLabelHQ/RecompOne · Licença: **MIT** · Linguagem: **C#**
> Maturidade: **51 commits, 188 stars, 1 mantenedor**, sem releases. Analisado em 2026-07-19.
> Inspirado em N64Recomp e XenonRecomp (mesma família de "static recompilers").

## O que é (com precisão)

RecompOne **traduz o executável MIPS do PS1 para C# antes da execução** (ahead-of-time) e fornece
um **runtime** que simula o ambiente do hardware PS1 em cima do .NET. Não é emulação instrução-a-
instrução: cada instrução MIPS vira código C# fixo que opera sobre um `CpuContext` + interface de
memória. Ex.: `addiu t0,t0,0x10` → `c.T0 = c.T0 + 0x10u;`.

- **Entrada:** imagem de disco (cue/bin) + **ELF/map de funções** (para localizar funções) + config JSON.
- **Saída:** um arquivo C# por segmento, compilável num app .NET nativo (Windows/Linux).
- **Runtime cobre:** BIOS (A/B/C), GPU (comandos + rasterizador), **GTE**, **SPU**, CD-ROM, **MDEC**,
  DMA, timers, interrupts, memory card, controle. E **reimplementa libs do PsyQ** (LibGpu, LibCd,
  LibEtc, LibPad) porque as originais dependem de interrupts que não funcionam bem sob recomp.
- **Overlays:** suportados (tabela de dispatch). **Nós não precisamos** — já confirmamos que o
  NASCAR Rumble é EXE único. Isso simplifica nossa config.
- **Patches:** dá pra substituir uma função inteira por C# nosso (`{"address":"800553C4","name":"..."}`)
  — para consertar código que o recompilador não trata (ex.: código automodificável) ou features.
- **Modding embutido:** `HookManager`, `ModLoader`, `SymbolRegistry`, atributos — um SDK de mods no lado PC.

## Estrutura do repo (para sabermos onde mexer)

```
RecompOne.Recompiler/   # o tradutor MIPS->C#
  Psx/PsxExe.cs, Parser.cs, SystemCfg.cs   # lê PS-X EXE e SYSTEM.CNF (já mapeamos ambos!)
  Elf/ElfReader.cs, Map/MapReader.cs, Config/FunctionMapLoader.cs  # <- entrada de símbolos
  Analysis/FunctionDetector.cs, JumpTable*.cs                       # acha funções e jump tables
  CodeGen/*.cs, Disasm/MipsDisasm.cs                                # emissão de C#
RecompOne.Runtime/      # o "platform layer" genérico do PS1
  Hardware/Gte.cs, Spu.cs, Mdec.cs, Interrupts.cs, Timers.cs
  Gpu/*.cs, Cdrom/*.cs, Bios/*.cs, sdk/Lib{Gpu,Cd,Etc,Pad}.cs
  Modding/*.cs          # hooks, mod loader
```

---

## O que isso AGREGA e ACELERA no nosso plano

### 1. É o terceiro caminho para "rodar sem emulador" — e o mais rápido
Antes eu classifiquei "recompilação estática" como imatura para PS1. **RecompOne É essa ferramenta**,
já funcional ("it can boot games"). Em vez de reescrever 943 arquivos à mão (como o ctr-native fez
via decomp), o RecompOne **traduz o EXE inteiro automaticamente**. Isso encurta drasticamente o
tempo até um primeiro boot nativo do NASCAR Rumble.

### 2. Nossas descobertas alimentam o RecompOne diretamente
- Ele precisa de **ELF/map de funções** → é exatamente o produto da Fase 4 (Ghidra → FUNCTION_MAP).
  Ghidra exporta ELF e mapa de símbolos que o `MapReader`/`FunctionMapLoader` consome.
- Ele lê **PS-X EXE e SYSTEM.CNF** → já mapeamos os dois (load 0x80010000, entry 0x800A5440).
- **Sem overlays** no nosso jogo → a config fica simples (nada de dispatch table).
- Nosso `ISO_TREE.md` já tem o layout do disco para preencher a config.

### 3. Substitui a necessidade de construir o "platform layer" do zero
O `RecompOne.Runtime` já é o facade de hardware PS1 (GTE/GPU/SPU/CD/MDEC) que, no caminho
ctr-native, teríamos que escrever ou adaptar. Aqui já vem pronto e **genérico** (serve a qualquer jogo).

### 4. Traz um SDK de mods no lado PC "de brinde"
`Modding/HookManager + ModLoader` permite mods em C# sobre o jogo recompilado — um complemento
à nossa Frente B, no ambiente nativo.

---

## Riscos e limites (análise honesta — não é bala de prata)

1. **Maturidade baixa.** 51 commits, 1 mantenedor, sem releases. O próprio autor diz: *"I wouldn't
   say this tool is ready to make actual recomps but it can boot games."* Apostar todo o port nele
   é apostar numa ferramenta jovem. Mitigação: usar como **trilha paralela**, não como única via.
2. **Recomp ≠ decomp.** A saída C# é gerada automaticamente e **ilegível** — dá um jogo que *roda*,
   mas **não gera entendimento**. Isso colide com o Princípio #1 do PRD ("compreender antes de
   modificar"). Conclusão: RecompOne acelera o **PORT**, mas **não substitui** o Ghidra para
   entender física/IA/formatos e fazer mods significativos.
3. **Quirks específicos do jogo.** Código automodificável, timing sensível a interrupts, e o
   streaming de áudio/vídeo da EA (`.WVE` VLC0, `.AV` SWVR/VAG) podem não "cair" no runtime padrão
   (MDEC/SPU genéricos). Provável necessidade de **patches** manuais nessas áreas.
4. **Saída em C#/.NET**, não C. Ótimo para PC multiplataforma, mas é um stack diferente do
   ctr-native (C17+SDL3). Decisão de arquitetura, não defeito.
5. **⚠️ Postura anti-IA do autor.** O README é explícito: *"AI was not involved in writing the code...
   This project does not support vibe-coded ports... I will not provide help for ports produced that
   way."* A licença MIT **permite** usarmos a ferramenta com auxílio de IA, mas **não teremos suporte
   da comunidade upstream** para trabalho assistido por IA. Devemos ser transparentes e auto-suficientes;
   contribuir de volta com correções bem-feitas e revisadas por humano é o caminho respeitoso.

---

## Como encaixa no plano: DUAS TRILHAS PARALELAS

| Trilha | Ferramenta | Entrega | Serve a |
|---|---|---|---|
| **A — Entendimento** | Ghidra + nossos parsers | FUNCTION_MAP, RAM_MAP, formatos, mods PS1 | Princípio #1, Frentes A/B/C |
| **B — Port rápido** | **RecompOne** | build nativo (.NET) que dá boot | objetivo "rodar sem emulador" |

**Sinergia:** a Trilha A produz o **map de funções** que a Trilha B consome; a Trilha B dá um
**ambiente C# vivo** para testar hipóteses e escrever patches; cada patch de RecompOne fica melhor
com o entendimento vindo do Ghidra. Elas se retroalimentam.

## Revisão do prazo do "executável sem emulador"

Com o RecompOne existindo, reviso a estimativa que dei antes (que assumia construir a tooling do zero):

- **Primeiro boot nativo (tela inicial, com falhas):** plausível em **semanas a poucos meses** APÓS
  termos um map de funções decente (Fase 4) e a config montada — não anos.
- **Jogável (menu + uma corrida rodando, com bugs):** **meses**.
- **Port estável/polido (áudio, vídeo EA, física fiel, sem travar):** ainda provavelmente **~1 ano+**,
  por causa dos quirks do jogo + imaturidade da ferramenta.

Ou seja: o RecompOne **não elimina** o trabalho, mas troca "anos construindo um recompilador" por
"meses adaptando um recompilador existente". É a maior aceleração possível para a sua meta.

## Status "RecompOne-ready" (2026-07-22) — ✅ pronto para tentar o boot

Revisitado com o progresso da Fase 4 (Ghidra). **Agora temos exatamente o que o RecompOne consome.**

- Repo **ativo** (atualizado 2026-07-22, 337 stars). Uso: `recompone <config>.json`.
- **.NET 8 instalado** (8.0.416) → dá para compilar/rodar o recompilador (é C#).
- Formato de config (de `ConfigLoader.cs`): `cue`, `elf`/`map`/**`funcMap`**, `main`, `overlays`,
  `stubs`, `ignored`, `patches`, `linearSweep`. O **`funcMap`** é um JSON `functions[]` com
  `address`(hex), `name`, `size` — **idêntico ao nosso export do Ghidra** (`ghidra_out/functions.csv`).
- **Artefatos gerados** (a partir do nosso Ghidra):
  - `recompone/nascar_funcmap.json` — **1855 funções** do texto do EXE (0x80010030–0x800a9be8),
    568 já nomeadas (PsyQ + nosso trabalho).
  - `recompone/nascar.json` — config: aponta o `.cue`, o funcMap, `main=800a5440`, **sem overlays**.
- **NASCAR Rumble é EXE único (sem overlays)** → dispensa a parte mais complexa (dispatch de overlay).

### Plano para o 1º boot (Trilha B)

1. `git clone` do RecompOne e `dotnet build`.
2. `recompone recompone/nascar.json` → gera C# (um arquivo por segmento) usando nosso funcMap.
3. `dotnet build`+`run` do projeto gerado (runtime = GTE/GPU/SPU/CD já prontos) → tentar o boot.
4. Catalogar o que quebra → escrever `patches` (C#) para funções problemáticas (código
   automodificável, quirks do streaming EA). Iterar.
> Expectativa realista: 1º boot (com falhas) plausível; polimento é longo. Respeitar a postura
> anti-IA do autor (não pedir suporte upstream para trabalho assistido por IA).

## Ações concretas

1. ✅ Manter a Fase 4 (Ghidra) como prioridade — ela é pré-requisito das DUAS trilhas.
2. 🔵 Fazer o Ghidra exportar **ELF + map de símbolos** num formato que o `MapReader` do RecompOne aceite.
3. 🔵 Montar um `nascar-rumble.json` de config do RecompOne (disco + EXE; sem overlays) usando o `ISO_TREE.md`.
4. 🔵 Tentar um **primeiro boot** cedo (marco motivacional) e catalogar o que quebra → vira lista de patches.
5. ⚖️ Estudar `Runtime/Hardware/{Gte,Spu,Mdec}.cs` para prever o suporte ao streaming de áudio/vídeo EA.
6. 🤝 Se contribuirmos upstream, respeitar a postura do projeto: código revisado por humano, sem "vibe-code".

## Comparação das três referências

| | ctr-native | RecompOne | decomp manual (CTR-ModSDK) |
|---|---|---|---|
| Método | decomp→C17+SDL3 | recomp automática MIPS→C# | reescrita humana em C |
| Velocidade até boot | anos | **semanas-meses** | anos |
| Gera entendimento? | sim | **não** | sim (máximo) |
| Fidelidade final | alta | média (depende de patches) | máxima |
| Esforço | altíssimo | **médio** | altíssimo |

**Recomendação:** RecompOne vira nossa **Trilha B (port rápido)**, rodando em paralelo à Trilha A
(Ghidra/entendimento), que continua sendo o coração do projeto e o que alimenta o RecompOne.

## Tentativa de 1º boot (2026-07-22) — recompilação ✅, boot bloqueado pela janela (macOS)

Executado o pipeline completo com nossos artefatos do Ghidra:

1. ✅ **Recompilador compilou** (.NET 10; instalei `dotnet-install --channel 10.0`).
2. ✅ **`recompone recompone/nascar.json` rodou** — leu SYSTEM.CNF/PS-EXE (PC=0x800A5440,
   load=0x80010000, batendo com nossa análise), processou **1855 funções** do nosso funcMap,
   achou 44 jump tables, aplicou 20 reimplementações PsyQ, e **gerou `Recompiled/main.cs`
   (188.902 linhas de C#) + Entry.cs + Stubs.cs**.
3. ✅ **Host compilou** (`recompone/host/`: projeto que referencia `RecompOne.Runtime` + inclui o
   C# gerado; chama `Recompiled.Entry.Run(mem, cue)`). **188k linhas, 0 erros.**
4. ❌ **Boot travou** com `EXC_BAD_ACCESS` em `glfwSetWindowPos` (**GLFW**): a criação da janela
   falhou no **macOS ARM** (retornou nulo) e o runtime tentou posicioná-la. É um problema de
   **portabilidade da camada de janela/gráfico do RecompOne no macOS**, NÃO da nossa recompilação.

**Conclusão:** a ponte Ghidra → RecompOne funciona de ponta a ponta — o MIPS do NASCAR Rumble
virou C# nativo compilável a partir da NOSSA engenharia reversa. O único bloqueio é o windowing
(GLFW/OpenGL) no macOS. Caminhos: (a) rodar no **Windows** (alvo primário do RecompOne); (b) patch
no `HostWindow` do RecompOne para macOS (checar retorno nulo do glfwCreateWindow / hints de GL).

Reprodução:
```bash
export PATH="$HOME/.dotnet:$PATH"; export DOTNET_ROOT="$HOME/.dotnet"
dotnet tools/RecompOne/RecompOne.Recompiler/bin/Release/net10.0/recompone.dll recompone/nascar.json
cd recompone/host && dotnet build -c Release && bin/Release/net10.0/NascarRumbleNative
```
