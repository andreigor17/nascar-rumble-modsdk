# Análise de Projetos de Referência (CTR) e o que aproveitar

> Analisado em 2026-07-19. Objetivo: decidir o que reusar (metodologia, tooling, arquitetura)
> no projeto NASCAR Rumble, e o que NÃO é reusável.

## Os quatro projetos e seu papel

| Projeto | O que é | Vale para nós |
|---|---|---|
| **[psx-modding-toolchain](https://github.com/mateusfavarin/psx-modding-toolchain)** | Build system **game-agnostic** para mods de PS1 | ⭐ **Adotar como nosso build/patch system** |
| **[CTR-ModSDK](https://github.com/CTR-tools/CTR-ModSDK)** | SDK + decomp do CTR, montado *sobre* a toolchain acima | ⭐ **Template de estrutura de repo e workflow** |
| **[ctr-native](https://github.com/CTR-tools/ctr-native)** | Port nativo PC do CTR (C17 + SDL3) sobre a decomp | ⭐ **Template de arquitetura do port (Fase 10)** |

## Regra de ouro: reusar MÉTODO e FERRAMENTA, não CÓDIGO de jogo

**CTR é da Naughty Dog; NASCAR Rumble é da EA.** Engine diferente, formatos diferentes.
Nosso container `CTRL/SHOC/SHDR` (EA) não tem nada a ver com os formatos do CTR. Portanto:

- ❌ **Não reusável:** parsers de formato, código decompilado do jogo, structs, símbolos do CTR.
- ✅ **Reusável:** o build system, a metodologia de decomp, a estrutura de repositório, e —
  crucialmente — a **camada de plataforma PS1** do ctr-native (o hardware do PS1 é o mesmo
  para qualquer jogo).

---

## 1. psx-modding-toolchain — ADOTAR (economiza a maior parte da Frente B)

É exatamente o "Patch Builder" das Fases 3/9 do nosso plano, **já pronto e testado**. Oferece:

- Compilador **gcc-mipsel-none-elf** (13.1.0) para injetar código C em endereços de RAM específicos.
- Injeção por **overlay/seção**: cada trecho de C compila para um endereço-alvo, declarado no
  `buildList.txt` (versão, seção, endereço RAM, offset no arquivo, fonte).
- **Reconstrução de ISO** via mkpsxiso a partir de `disc.json` (mapa de arquivos do disco).
- **Hot-reload** com PCSX-Redux (testar mudança de código/asset durante o jogo).
- **Substituição de textura** por PNG com convenção de nome `nome_x_y_clutx_cluty_w_h_bpp`.
- Distribuição de mods como **patches xdelta** (nunca a ISO — bate com nosso princípio #4).

### Como plugar o NASCAR Rumble (game-agnostic)

Criar `games/nascar-rumble/` com subpastas `build/ include/ mods/ plugins/ symbols/` e dois arquivos:

- **`config.json`** — nome da ISO e flags (ex.: `function_sections`, `reorder_functions`, `ldflags`).
- **`disc.json`** — estrutura do disco: cada seção com `name` (alias do arquivo), endereço RAM e
  offset. É aqui que declaramos `SLUS_010.68`, `GLBLDATA.PSX`, os `.TRK`, etc.

Fluxo: colocar a ISO em `build/`, rodar Extract → editar/compilar mods (`buildList.txt`) → Build ISO.

> **Consequência para o plano:** não vamos escrever nosso próprio Patch Builder do zero.
> Adotamos essa toolchain e focamos nossa energia na engenharia reversa (o que é único do NASCAR).

## 2. CTR-ModSDK — template de estrutura e workflow

Espelhar a organização de repo, que já é pensada para evoluir até a decomp:

```
decompile/   # funções reescritas em C (a partir do Ghidra)
ghidra/      # disassembly organizado (EXE principal + overlays numerados)
symbols/     # mapa de memória e símbolos  (nosso RAM_MAP + FUNCTION_MAP viram isto)
mods/        # mods de exemplo, cada um documentado
rebuild_PS1/ # build da ISO PS1
rebuild_PC/  # build do port nativo (futuro)
tools/       # utilitários
```

**Workflow de decomp (o loop que vamos seguir):** reescrever UMA função em C → compilar isolada →
**verificar que bate byte-a-byte** com a original → integrar em `decompile/`. Esse ciclo de
"matching" é o coração da Fase 10.

## 3. ctr-native — template do port nativo (o endgame)

Prova que o port é real e mostra COMO se chega lá. Arquitetura:

- **C17**, alvo Windows/Linux, **SDL3** compilado junto (executável único, zero dependências).
- **`game/`** = 943 arquivos de código decompilado (a lógica do jogo).
- **`platform/`** = camada que **reimplementa o hardware do PS1** sem emular: áudio, input,
  memory card, CD e um *facade* do PSX que traduz primitivas de GPU em "tokens nativos de 24-bit".
- Precisa do disco original para os **assets** (não redistribui conteúdo).
- **6.621 commits, 943 arquivos** → confirma a estimativa: um port é trabalho de **anos**.

**O que dá pra aproveitar de verdade:** a `platform/` lida com o **hardware do PS1, que é
idêntico** no NASCAR Rumble. A camada que traduz `libgpu`/`libspu`/`libcd` para SDL3 é, em
grande parte, independente do jogo. Estudar (e, se a licença permitir, adaptar) essa camada
nos pouparia a parte mais difícil e demorada de um port futuro.

> **Port = decomp (lógica única do jogo) + platform layer (hardware PS1, reaproveitável).**
> A metade "platform" já existe como referência; a metade "game" é o que construímos nas Fases 4–9.

---

## Impacto no nosso plano

| Fase | Antes | Depois desta análise |
|---|---|---|
| 3 (ISO Explorer) | ferramenta própria | manter a nossa p/ análise; extração de ISO pode usar a toolchain |
| 9 (Patch Builder) | construir do zero | **adotar psx-modding-toolchain** |
| 10 (Port) | pesquisa aberta | seguir arquitetura ctr-native (C17+SDL3, game/ + platform/) |
| Estrutura repo | nossa | alinhar com CTR-ModSDK (`decompile/ symbols/ rebuild_*`) |

## Ações concretas (próximos passos)

1. ✅ **NASCAR Rumble NÃO usa overlays** (confirmado 2026-07-19). O `SLUS_010.68` é um EXE único:
   load `0x80010000`, tamanho `0x9F800` (~640 KB), fim em `0x800AF800`, entry `0x800A5440`.
   Zero menções a "OVERLAY"/".OVL" nas strings. **Isso é mais simples que o CTR** (que troca
   overlays numerados na RAM): nossa decomp e injeção miram um único espaço de endereços plano.
   Bônus: o EXE ainda tem **strings de debug printf** (`%s: dir was not found`, `%s timeout:`,
   `%s%s%ld%c.lsc`, `GlblData.psx`, `BB1.trk`…) — cada uma nomeia a função que a referencia,
   acelerando muito o `FUNCTION_MAP.md` no Ghidra.
2. 🔵 **Identificar o compilador original** (provável PsyQ) — necessário para decomp "matching".
3. ✅ **Adotar a toolchain:** clonar psx-modding-toolchain e criar `games/nascar-rumble/` com
   `config.json` + `disc.json` (usar nosso `ISO_TREE.md` para preencher os offsets/LBAs).
4. ⚖️ **Checar licenças** de psx-modding-toolchain e ctr-native antes de reusar código da
   `platform/` (metodologia e uso da toolchain são livres; reuso de código exige conferir licença).

## Diferenças-chave CTR × NASCAR Rumble (para não errar)

- Engine e formatos totalmente distintos (Naughty Dog vs EA). Reuso = método/tooling, não código.
- CTR tem comunidade de decomp madura; nós partimos do zero na parte específica do jogo.
- Se o NASCAR for EXE único (sem overlays), várias coisas ficam mais fáceis que no CTR.
