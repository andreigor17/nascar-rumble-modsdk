# Estado persistente do projeto

> Este é o ponto de retomada entre sessões. Antes de iniciar trabalho novo, leia este arquivo e
> `docs/PLANO_DE_EXECUCAO.md`. Uma etapa só recebe `CONCLUÍDA` após seus testes e *gate* passarem.

## Etapa atual

- **Etapa 0 — Congelar referência e evidências: CONCLUÍDA em 2026-10-06**
- **Etapa 1 — Identificar compilador, assembler, linker e flags: CONCLUÍDA em 2026-10-06**
- **Etapa 2 — Esqueleto reproduzível e split integral: CONCLUÍDA em 2026-10-06**
- **Etapa 3 — Loop produtivo por função: CONCLUÍDA em 2026-10-06**
- **Etapa 4 — Métricas, validação local e governança: CONCLUÍDA em 2026-10-07**.
- **Etapa 5 — Boot original visível: EM ANDAMENTO**.
- Decisão do mantenedor em 2026-10-07: não armazenar a cópia do jogo na nuvem e não usar GitHub
  Actions neste momento. O código continua versionado no Git; antes de cada envio, os gates rodam
  localmente com a cópia legal existente no Mac.
- Autorização permanente do mantenedor em 2026-10-07: sempre que um marco real for concluído e
  validado localmente, publicar manualmente a atualização do site. Isso não autoriza GitHub Actions
  nem testes remotos; a publicação usa a branch `gh-pages` conforme `docs/SITE_DEPLOY.md`.
- Prioridade do mantenedor em 2026-10-07: jogo original jogável primeiro. Mods, melhorias gráficas
  e novas resoluções ficam depois de menu e corrida original estáveis; o carregador de mods do host
  nativo permanece desligado por padrão.
- Trilha nativa: `NascarRumbleNative` abre no macOS ARM, lê e decodifica a tela legal, carrega
  `CW/OPENING/INTRO.WVE` e já apresenta visualmente o primeiro trecho da intro (logo vermelho da
  EA). O próximo bloqueio é um underflow do buffer de áudio após aproximadamente 15 quadros; o
  menu ainda não foi alcançado.
- Os avisos “NascarRumbleNative encerrou inesperadamente” vistos no Mac vieram das execuções de
  diagnóstico de 2026-10-07: os relatórios indicam `SIGABRT` após exceção .NET não tratada, com o
  processo de desenvolvimento como pai. Não existe LaunchAgent ou processo relançando o host. O
  host agora captura falhas gerenciadas, encerra o runtime e retorna código de erro controlado.

## Registro

### Etapa 0 — Congelar referência e evidências

Status: **CONCLUÍDA — gate aprovado em 2026-10-06**

Entregas preparadas:

- `config/reference_hashes.json`: tamanho, SHA-1 e SHA-256 do BIN, CUE e EXE.
- `scripts/verify_reference.py`: valida os artefatos e campos do cabeçalho PS-X EXE.
- `config/toolchain_observed.json`: snapshot do ambiente disponível e ferramentas ausentes.
- `experiments/grid/championship_gold_rush.json`: evidência estruturada da captura do grid.
- `scripts/verify_grid_capture.py`: cruza captura, layout e catálogo de carros.
- `tests/test_stage0.py`: testes positivos e negativos da etapa.

Validação executada:

```text
python3 scripts/verify_reference.py
  PASS — 3/3 artefatos; tamanhos, SHA-1, SHA-256 e cabeçalho PS-X EXE

python3 scripts/verify_grid_capture.py
  PASS — 6/6 entradas; nomes, IDs, tipos e posições

python3 -m unittest discover -s tests -v
  PASS — 6 testes

python3 -m py_compile scripts/verify_reference.py scripts/verify_grid_capture.py tests/test_stage0.py
  PASS

git diff --check
  PASS
```

Observação: a primeira validação revelou nomes divergentes da fonte `cars_wiki.csv`; a fixture foi
corrigida e toda a suíte foi repetida com sucesso. Nenhum dump, savestate ou asset foi versionado.

### Etapa 1 — Identificar compilador, assembler, linker e flags

Status: **CONCLUÍDA — gate aprovado em 2026-10-06**

Primeiras ações obrigatórias:

1. selecionar corpus de 15–30 funções pequenas e representativas a partir de `functions.csv`;
2. separar candidatas de código do jogo das bibliotecas PsyQ;
3. localizar/registrar toolchains candidatas com versão e checksum;
4. produzir comparação objetiva por função para versões e flags;
5. só concluir após cinco funções próprias matched e um módulo relinkado previsivelmente.

Progresso em 2026-10-06:

- `config/compiler_corpus.json`: 23 funções próprias prováveis selecionadas, cobrindo funções folha,
  stores, branches, aritmética, globals, listas e índices escalados.
- `config/psyq_candidates.json`: PsyQ 4.3 e 4.4 inventariados por commit/checksums.
- Wibo 1.2.0 para macOS validado pelo SHA-256 oficial; Wine não foi usado porque seu cask está
  desabilitado no Homebrew atual por Gatekeeper.
- `tools/compiler_probe/probe.c` + `scripts/compiler_probe.py`: compilação, montagem, parser de
  objetos PsyQ LNK e comparação byte a byte com o EXE.
- Resultado: **10 funções próprias matched** com `-O2 -G0 -g0` tanto em PsyQ 4.3 quanto 4.4.
- Duas formulações C adicionais ainda diferem; permanecem como probes exploratórios e não contam.

Conclusão final:

- Corpus ampliado para 24 funções.
- Dez funções próprias pequenas matched byte a byte.
- Probe discriminador `0x80078c24` (36 bytes, stack + chamada externa): PsyQ 4.3 matched; PsyQ
  4.4 diferiu no delay slot do epílogo. Compilador identificado como GNU C 2.7.2.SN32.3.7.
- Matriz `O1/O2 × G0/G8`: O2 vence no corpus aplicável; o discriminador confirma `-O2 -G0 -g0`.
- ASPSX 2.56 validado; PSYLINK 2.73 relinkou módulo mínimo previsivelmente.
- Duas execuções do linker produziram CPE idêntico com SHA-256
  `3617f0369cb3469593d9dc375979eb21d8d3d2138faaf60e54ccf58ef54bce21`.
- Toolchain congelada em `config/toolchain.lock.json`; análise em `docs/TOOLCHAIN.md`.

O jogo usa acessos absolutos e relativos a `gp`; isso indica `-G` por módulo/objeto. A baseline
validada é G0, e a classificação dos módulos G8 passa a ser parte da Etapa 2, não uma pendência do
gate de identificação.

### Etapa 2 — Esqueleto reproduzível e split integral

Status: **CONCLUÍDA — gate aprovado em 2026-10-06**

Primeiras ações obrigatórias:

1. instalar e fixar Splat e dependências por versão/checksum;
2. descrever header, `.text`, `.rodata`, `.data`, `.sdata` e `.bss` iniciais;
3. importar símbolos confirmados do Ghidra;
4. gerar árvore ASM integral;
5. obter primeiro relink híbrido e comparar regiões/EXE.

Conclusão:

- Splat 0.50.0 e 12 dependências fixados com hashes em `requirements-splat.lock`; commit e
  binutils MIPS 2.47 registrados em `config/splat_toolchain.lock.json`.
- Mapa inicial registra header, envelope `.text`, `.rodata`, `.sdata`, `.data`, BSS observado em
  `0x800AF538..0x800BCEE8` e padding final do payload.
- As 1.855 funções do intervalo do EXE foram importadas do Ghidra; a árvore gerada cobre todo o
  código/dados e permanece git-ignored/reproduzível.
- Inventário `config/gp_usage.json`: 503 funções com evidência positiva de acesso `$gp`; 1.352
  permanecem não classificadas até que fronteiras de objeto sejam confirmadas.
- `make setup`, `make extract`, `make build` e `make check` executados em sequência; rebuild com
  655.360 bytes e SHA-256 idêntico `e90e3c7e4cf286a7a0a5e827b3a404bfe8407b15f8b2fd54536d426682b20f75`.
- Testes automatizados e `git diff --check` passam. Detalhes em `docs/SPLIT_BUILD.md`.

Limite conhecido: o envelope `.text` ainda contém ilhas de dados e as fronteiras finas de objetos
originais não foram provadas. O build conserva esses bytes integralmente em ASM; o refinamento deve
acompanhar a conversão por função sem reduzir o match.

### Etapa 3 — Loop produtivo por função

Status: **CONCLUÍDA — gate aprovado em 2026-10-06**

Conclusão:

- asm-differ, objdiff 3.8.2, MASPSX, PsyQ SDK e Wibo instalados de fontes fixadas por
  commit/versão e SHA-256 em `config/decomp_tools.lock.json`;
- `make diff FUNC=...`, `make objdiff FUNC=...`, `make context FUNC=...`, `make backlog` e
  `make progress` testados no fluxo real;
- `config/function_backlog.csv` cobre 1.855 funções e registra endereço, tamanho, instruções,
  callers/callees, strings, `$gp`, status, responsável e scratch;
- o contexto local inclui disassembly, bytes e metadados; anexa C do Ghidra quando a exportação
  local existe, mas funciona sem ela e sem sessão manual do Ghidra;
- `FUN_80078c24` substituída por C PsyQ 4.3 (`-O2 -G0 -g0`): 36/36 bytes ligados, 100% estrutural
  no objdiff e executável completo com SHA-256 idêntico;
- uma candidata folha de 31 instruções foi trabalhada, mas corretamente mantida fora do split ao
  não atingir match, demonstrando a política de integração sem regressão.

Validação executada:

```text
make extract && make build && make check
  PASS — SHA-256 e90e3c7e4cf286a7a0a5e827b3a404bfe8407b15f8b2fd54536d426682b20f75

make diff FUNC=FUN_80078c24
  PASS — 9/9 instruções iguais

make objdiff FUNC=FUN_80078c24
  PASS — 100.0% structural match
```

Detalhes de uso e política em `docs/DECOMP_WORKFLOW.md`.

### Etapa 4 — Métricas, validação local e governança

Status: **CONCLUÍDA — gate local aprovado e política definida em 2026-10-07**

Entregas:

- `progress.json` determinístico mede separadamente código/funções C matched, dados reconstruídos,
  ASM de funções restante, símbolos e cobertura explicitamente classificada por subsistema;
- `config/progress_baseline.json` e testes rejeitam regressões de match;
- README e site consomem o manifesto, sem percentuais matching duplicados manualmente;
- `CONTRIBUTING.md`, template de PR e `docs/PROGRESS_AND_CI.md` fixam setup, convenções, política
  non-matching e separação legal dos assets;
- binutils 2.47, toolchain de decomp, Wibo e dependências permanecem fixados por versão/commit e
  SHA-256.

Validação local executada:

```text
make ci-public
  PASS — lint de config, formato, progress.json e suíte pública (gates proprietários pulados)

make ci-full
  PASS — split, build, todos os gates e SHA-256
  e90e3c7e4cf286a7a0a5e827b3a404bfe8407b15f8b2fd54536d426682b20f75

make docker-matching
  PASS — VM Colima x86-64/QEMU, imagem linux/amd64 e o mesmo SHA-256 byte a byte

cd site && npm run build
  PASS — 36 páginas
```

Métricas publicadas: 36/596.188 bytes de funções C matched; 1/1.855 funções; 22.852/22.852
bytes de dados reconstruídos; 596.152 bytes de funções ainda em ASM; 1.855 símbolos. Os dados em
ASM serem byte-idênticos não significa que estejam compreendidos ou tipados.

Política vigente: `make ci-public` e `make ci-full` rodam no Mac antes de cada push. Nenhum BIN,
CUE, EXE ou bundle do jogo é enviado ao GitHub. Os workflows do GitHub Actions foram removidos;
por enquanto o GitHub é usado somente para preservar e compartilhar o código.

### Etapa 5 — Boot original visível

Status: **EM ANDAMENTO — primeiro quadro visível; intro completa e menu ainda pendentes**

Estado observado no macOS ARM:

- executável nativo abre uma janela OpenGL 1280×748;
- entra no `main` recompilado e inicializa heap, interrupções, memory cards, controles, GPU, SPU e CD;
- localiza `CW/OPENING/LEGAL.LSC` no LBA 97407, com 35.136 bytes, e entrega seus 18 setores;
- decodifica as duas imagens da tela legal via MDEC (160 macroblocos e 30.720 palavras cada) e
  executa as transferências para a GPU com fallbacks OpenGL compatíveis com macOS;
- agenda cooperativamente callbacks de memory card, VBlank, CD e DMA sem o estouro de pilha que a
  conclusão síncrona da DMA de SPU causava;
- localiza `CW/OPENING/INTRO.WVE` no LBA 93447, carrega áudio/vídeo e decodifica quadros MDEC de
  280 macroblocos e 53.760 palavras;
- apresenta na janela o primeiro trecho real do vídeo, confirmado visualmente pelo logo vermelho
  da EA em 2026-10-07;
- a reprodução ainda para depois de aproximadamente 15 quadros por underflow do ring buffer de
  áudio (`available=832`, `required=3360`); intro completa, menu e jogo controlável permanecem
  pendentes.

Validação executada:

```text
python3 -m unittest tests.test_native -v
  PASS — 5 testes

make native-build
  PASS — NascarRumbleNative compilado para macOS arm64

execução local com a cópia legal
  PASS — primeiro trecho de INTRO.WVE visível na janela (logo EA)
```

Próximo gate: corrigir o abastecimento assíncrono do ring buffer de áudio, reproduzir a intro sem
parar e seguir até o menu aceitar input. A decomp matching permanece disponível para esclarecer
funções necessárias; trabalho de mods está suspenso.

Ponto exato de retomada para a próxima sessão:

1. Não reabrir os bloqueios de memory card, callbacks de CD, VBlank ou reentrância de DMA: eles já
   foram atravessados e estão cobertos por `NativeHooks.cs`, pelo patch local do RecompOne e pelo
   funcmap.
2. `FUN_80096e90` consome o áudio da intro. O hook `IntroAudioPoll` bombeia até 64 callbacks de CD
   antes de entrar na espera original, o que permite avançar aproximadamente 15 quadros, mas a
   leitura acaba em `read=16832`, `write=2304`, `available=832`, `required=3360`.
3. Investigar por que `LibCd.Tick()` deixa de aumentar o ponteiro de escrita nesse ponto: confirmar
   `_readActive`, `_readGeneration`, posição/LBA e se `intro_cd_ready_callback` consumiu o setor.
   A correção desejada é manter o produtor do ring buffer assíncrono/cooperativo, não ignorar o
   áudio nem substituir a intro por um atalho.
4. Para reproduzir: `make native-build` e depois `make native-run`. Para filtrar o diagnóstico,
   usar `RUMBLE_NATIVE_TRACE=1` e observar MDEC/CD e a linha `intro audio underflow`.
5. O primeiro quadro já foi confirmado. O próximo critério visual é a intro continuar se movendo;
   depois disso, seguir até o menu e validar input.

## Protocolo para finalizar uma etapa

1. Executar todos os testes relevantes e o *gate* descrito no plano.
2. Registrar comandos, resultados e limitações neste arquivo.
3. Alterar o status para `CONCLUÍDA` somente se não restar requisito obrigatório.
4. Marcar no plano a etapa concluída e indicar a próxima etapa exata.
5. Não tratar documentação, protótipo ou teste parcial como conclusão.
