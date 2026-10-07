# Plano de Execução — NASCAR Rumble Decompilation & ModSDK

> Revisão rigorosa: 2026-10-06. Alvo primário: `SLUS_010.68` (NTSC-U).
> O plano de 2026-07-19 foi substituído: várias fases exploratórias já terminaram, mas a
> infraestrutura essencial de uma *matching decomp* ainda não existe.

## 1. Estado real

### Já concluído ou comprovado

- ISO mapeada (108 arquivos); PS-X EXE extraído e identificado.
- Executável único, sem overlays conhecidos: carga `0x80010000`, entrada `0x800A5440`.
- PsyQ 4.6 identificado; 2.008 funções detectadas no Ghidra e 1.855 exportadas ao RecompOne.
- Container EA, `.LSC`, `Cpag` e `Ctrk` possuem entendimento útil.
- RAM, velocidade, roster de 168 carros, recursos e grid possuem pontos confirmados.
- RecompOne gera e compila C#, mas o primeiro boot ainda trava no host GLFW/macOS.
- Toolchain PsyQ identificada por matching: GNU C 2.7.2.SN32.3.7, `-O2 -G0 -g0` na baseline,
  ASPSX 2.56 e PSYLINK 2.73.
- Splat e build híbrido reproduzem `SLUS_010.68` byte a byte a partir de ASM/dados.
- O último commit (`9fef458`) documentou corretamente Single Race × Championship. A pesquisa
  posterior já localizou `grid_build` (`0x8008927c`), tabela `0x800b0e40` e `grid_spawn`
  (`0x8003132c`); portanto, o “próximo passo” daquele commit já foi superado no worktree.

### Lacunas restantes para uma decomp produtiva

- fronteiras finas de objetos e ilhas de dados ainda provisórias;
- conversão gradual do ASM em C matching;
- ciclo por função com `asm-differ`/`objdiff`/decomp.me;
- métricas de bytes/funções matched, dados e ASM restante;
- CI para build, checksums, testes, formato e regressão de progresso;
- testes dos parsers e experimentos dinâmicos;
- estrutura e convenções que permitam colaboração paralela.

**Diagnóstico:** a base de *matching decomp* agora existe. O maior acelerador passa a ser um loop
por função no qual o ASM possa ser convertido em C e verificado sem preparação manual repetitiva.

## 2. O que os projetos de referência ensinam

| Projeto | Prática que acelera | Aplicação aqui |
|---|---|---|
| [sotn-decomp](https://github.com/Xeeynamo/sotn-decomp) | Splat, configs versionadas, toolchain fixada, diff, permuter, hashes, progresso e CI | Modelo principal do pipeline |
| [silent-hill-decomp](https://github.com/shdecompilations/silent-hill-decomp) | Docker, compiladores/flags por segmento, `include_asm`, objdiff, checksums e convenções | Modelo para identificar toolchain e começar híbrido |
| [mgs_reversing](https://github.com/FoxdieTeam/mgs_reversing) | PsyQ real, Ninja, hash final, métricas por byte/função, variante `dev` e relançamento no PCSX-Redux | Referência mais próxima para build e iteração |
| [ctr-native](https://github.com/CTR-tools/ctr-native) | Separação `game/` × `platform/`, CMake/CTest e replay de bugs | Referência para o port, após uma base C estável |

Não copiar código/layouts de outras engines, complexidade de overlays nem a camada nativa antes da
hora. RecompOne continua útil como laboratório paralelo, mas não mede progresso da decomp.

## 3. Estratégia corrigida

1. **Matching decomp (caminho crítico):** binário → split → build híbrido ASM/C → diff → match.
2. **RE e mods (alimentadora):** Ghidra + PCSX-Redux produzem símbolos, tipos, testes e código C.
3. **Port (paralela e limitada):** RecompOne busca boot/jogabilidade; `ctr-native` orienta a
   arquitetura futura. Limitar esta trilha a ~20% do esforço até o build matching funcionar.

## 4. Ordem obrigatória

### Etapa 0 — Congelar referência e evidências — ✅ CONCLUÍDA (2026-10-06)

1. Registrar SHA-256/SHA-1 do BIN, CUE e `SLUS_010.68`; validar serial/região em todo build.
2. Gerar manifesto de Python, Splat, binutils, PsyQ, MASPSX e Wibo/Wine.
3. Converter a descoberta do grid em experimento reproduzível: script, ações, valores esperados e log.
4. Fazer documentação e site consumirem uma fonte de dados comum sempre que possível.

**Gate:** outro colaborador com a imagem correta obtém os mesmos hashes e artefatos gerados.

**Resultado:** gate aprovado por `scripts/verify_reference.py`, `scripts/verify_grid_capture.py` e
6 testes automatizados em `tests/test_stage0.py`. Evidências em `config/` e `experiments/grid/`.

### Etapa 1 — Identificar compilador, assembler, linker e flags — ✅ CONCLUÍDA (2026-10-06)

1. Separar código próprio, bibliotecas PsyQ e dados por assinaturas e padrões.
2. Criar corpus de 15–30 funções pequenas: leaf/non-leaf, switch, structs, signedness, `-G0/-G8`.
3. Testar versões/flags plausíveis de PsyQ/SN `cc1`; registrar diffs, não apenas suposições.
4. Determinar alinhamentos, small data, ordem de objetos e bibliotecas.
5. Fixar toolchain por checksum e documentar sua proveniência legal.

**Gate:** cinco funções próprias compilam exatamente e um módulo relinka previsivelmente. A versão
do SDK não prova, sozinha, a versão e as flags do compilador C.

**Resultado:** corpus de 24 funções; 10 funções pequenas matched; probe de 36 bytes com chamada e
stack distinguiu PsyQ 4.3 de 4.4 e confirmou `-O2 -G0 -g0`; módulo mínimo relinkado duas vezes pelo
PSYLINK 2.73 com CPE idêntico. `-G` varia por objeto e será classificado no split. Ver
`docs/TOOLCHAIN.md` e `docs/PROJECT_STATUS.md`.

### Etapa 2 — Esqueleto reproduzível — ✅ CONCLUÍDA (2026-10-06)

```text
config/       splat.yaml, símbolos, checksums
src/          C decompilado por subsistema
asm/          código ainda não convertido
include/      tipos PS1/PsyQ, structs e declarações
linker/       script e ordem de objetos
expected/     referência local, nunca assets no Git
tools/        split, build, diff e progresso
tests/        parsers e comportamento
```

1. Escrever config Splat e mapa inicial de `.text/.rodata/.data/.sdata/.bss`.
2. Importar símbolos confirmados do Ghidra; desconhecidos permanecem nomeados por endereço.
3. Gerar ASM para 100% do código ainda não convertido.
4. Relinkar com `include_asm`/objetos ASM antes de exigir código C.
5. Comparar cada segmento e o executável final com a referência.

**Gate:** `make setup && make extract && make build && make check` (ou equivalentes) reconstrói o
EXE byte a byte. Este marco transforma o repositório em uma decomp.

**Resultado:** Splat 0.50.0 e dependências fixados por versão/hash; 1.855 símbolos Ghidra
importados; inventário conservador de 503 funções com acesso relativo a `$gp`; ASM/dados cobrem
todo o payload; build de 655.360 bytes igual à referência, SHA-256
`e90e3c7e4cf286a7a0a5e827b3a404bfe8407b15f8b2fd54536d426682b20f75`. Ver
`docs/SPLIT_BUILD.md`.

### Etapa 3 — Loop produtivo por função — ✅ CONCLUÍDA (2026-10-06)

1. `asm-differ` para feedback local; contexto de decomp.me em um comando.
2. `objdiff` para comparação estrutural; permuter somente após o C estar correto.
3. Comandos únicos: `make diff FUNC=...`, `make context FUNC=...`, `make progress`.
4. Backlog com endereço, tamanho, callers/callees, strings, status, responsável e scratch.
5. Começar por funções de 20–150 instruções, folhas e utilitários; adiar `main`, GPU, física e
   grandes máquinas de estado.
6. Integrar somente com build válido, tipos razoáveis e sem regressão de match.

**Gate:** um colaborador produz um match sem reconstruir manualmente o contexto básico no Ghidra.

**Resultado:** asm-differ, objdiff, MASPSX, PsyQ e Wibo fixados por versão/commit e checksum;
`make diff`, `make objdiff`, `make context`, `make backlog` e `make progress` operacionais; backlog
de 1.855 funções com grafo de chamadas, strings e campos de colaboração; primeiro C integrado em
`FUN_80078c24`, com 100% no objdiff e EXE final idêntico. O progresso já oferece folhas de 20–150
instruções como próxima fila; uma tentativa de 31 instruções semanticamente correta não foi
integrada porque não atingiu match. Ver `docs/DECOMP_WORKFLOW.md`.

### Etapa 4 — Métricas, validação local e governança — ✅ CONCLUÍDA (2026-10-07)

1. Medir separadamente bytes de código matched, funções matched, dados matched, ASM restante,
   símbolos e cobertura por subsistema. “Funções detectadas” não conta como decompilação.
2. Gates locais: config/split lint, build matching, checksum, testes Python, formatação C/Python e
   proteção contra regressão de progresso.
3. Publicar `progress.json`; README e site consomem este arquivo, sem percentuais manuais.
4. Criar `CONTRIBUTING.md`, setup, convenções, template de PR e política non-matching.
5. Fixar dependências por commit/checksum; Docker para CI/Linux e Wibo/Wine para macOS.

**Gate:** antes de cada push, `make ci-public` passa; alterações de split/C também exigem
`make ci-full` e o checksum byte-idêntico usando a cópia legal local.

**Resultado:** `progress.json`, baseline anti-regressão, métricas por subsistema, Docker Linux,
gates locais público/full, guia de contribuição e template de PR foram implementados.
`make docker-matching` e `make ci-full` reconstruíram o executável com SHA-256 idêntico. Por
decisão do mantenedor, os testes da decompilação ficam locais e nenhum asset do jogo é enviado ao
GitHub. Ver `docs/PROGRESS_AND_CI.md`.

### Etapa 5 — Primeira fatia vertical: grid de campeonato

1. Decompilar e dar match em `rng_next`, `grid_build`, helpers e `grid_spawn`.
2. Definir structs do descritor de grid, modo e configuração do campeonato.
3. Criar variante **matching** e variante **dev/mod** que injeta IDs escolhidos.
4. Smoke test no PCSX-Redux: carregar estado, iniciar Championship, capturar tabela e validar
   IDs/contagem antes do spawn.
5. Empacotar o primeiro mod reproduzível sem conteúdo do jogo.

**Gate:** a lógica está matched em C, documentada, testada e usada por um mod.

### Etapa 6 — Escalar por subsistemas

Ordem sugerida:

1. runtime/libc/PsyQ e matemática;
2. alocação, listas e recursos (`res_find`, `res_register`);
3. CD/filesystem e container EA;
4. frontend, estado global e menus;
5. configuração de corrida, entidades e input;
6. física, colisão e IA;
7. GPU/render/HUD;
8. SPU, música e streaming EA;
9. save/memory card, FMV e periféricos.

Para cada subsistema: símbolos → tipos → funções pequenas → orquestradoras → testes → docs.

**Gate:** API/structs documentadas, funções classificadas, match medido, smoke test e nenhuma
dependência escondida apenas no projeto Ghidra.

### Etapa 7 — Formatos e SDK com round-trip

1. Transformar scripts em pacote Python instalável e CLI estável.
2. Fixtures mínimas próprias/sintéticas e testes unitários por parser.
3. Exigir `decode → encode → bytes idênticos` antes de habilitar escrita.
4. Validar limites, endian, offsets, alinhamento e dados malformados.
5. Integrar `dumpsxiso/mkpsxiso`, preservando LBA quando necessário.

**Gate:** rebuild sem alteração mantém hashes e todo editor possui teste de ida e volta.

### Etapa 8 — Port após massa crítica

1. Corrigir RecompOne quando o defeito revelar conhecimento reutilizável; catalogar patches.
2. Definir fronteira `game/` × `platform/` inspirada no `ctr-native`.
3. Auditar licença e pressupostos de ponteiros, GPU, áudio, CD e streaming antes de reutilizar código.
4. Iniciar port C dedicado somente com tipos centrais estáveis e parcela substancial de C decompilado.

**Gate:** menu e corrida completa passam por testes/replays determinísticos no host e PS1.

## 5. Sprint imediata

Não abrir outra frente de formato/gameplay antes de:

1. congelar hashes e toolchain;
2. criar `config/`, `src/`, `asm/`, `include/`, `linker/`, `tests/`;
3. produzir o split integral do `SLUS_010.68`;
4. relinkar build 100% ASM idêntico;
5. confirmar compilador/flags com funções pequenas;
6. substituir a primeira função ASM por C matched;
7. instalar diff, métricas e CI;
8. converter `grid_build` em fatia vertical decomp + mod + teste.

## 6. Indicadores corretos

- `% bytes .text matched` e `funções matched / total`;
- `% dados matched` por seção e bytes ASM restantes;
- funções nomeadas por confiança e structs com offsets verificados;
- testes, smoke tests e taxa de sucesso;
- último build com checksum idêntico;
- bloqueios de toolchain, linker e plataforma.

Não usar como progresso principal: páginas de docs, funções apenas detectadas no Ghidra, arquivos
extraídos ou C# gerado automaticamente pelo RecompOne.

## 7. Riscos

| Risco | Mitigação |
|---|---|
| Compilador/flags errados | corpus diferencial; non-matching separado |
| Segmentos incorretos | build ASM integral e linker antes de C em massa |
| Pesquisa dispersa | backlog por subsistema; descoberta deve virar símbolo/tipo/teste |
| Dependência do Ghidra local | mapas/headers versionados e sync automatizado |
| Port consumir o projeto | limite de esforço; matching é caminho crítico |
| Regressões silenciosas | checksum, diff por objeto, CI e baseline |
| Colaboração difícil | setup de um comando, fila de funções e guia |
| Questões legais | nenhuma ROM/asset; somente hashes, configs, código e fixtures próprias |

## 8. Definição de “chegar ao estágio dos outros”

O primeiro objetivo não é 100%. É obter o mesmo **sistema de produção**:

- build reproduzível verificado por hash;
- fonte híbrida C/ASM sempre executável;
- diff e status por função;
- progresso automático por bytes/funções;
- CI e convenções para colaboração;
- variante modificável testável rapidamente;
- matching, mods e port claramente separados.

Depois disso o avanço passa a ser acumulativo. Como o jogo não possui overlays conhecidos e o EXE
(~638 KiB) é comparável aos executáveis principais já concluídos pelo MGS reversing, a meta é
plausível — mas depende primeiro das Etapas 0–4.
