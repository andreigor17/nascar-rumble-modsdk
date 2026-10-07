# Plano de Execução — NASCAR Rumble Decompilation & ModSDK

> Revisão: 2026-10-07. Alvo primário: `SLUS_010.68` (NTSC-U).
> Decisão do mantenedor: entregar primeiro o jogo original jogável como aplicativo nativo.
> Melhorias gráficas, novas resoluções e mods permanecem posteriores à paridade funcional.

## 1. Estado real

### Já concluído ou comprovado

- ISO mapeada (108 arquivos); PS-X EXE extraído e identificado.
- Executável único, sem overlays conhecidos: carga `0x80010000`, entrada `0x800A5440`.
- PsyQ 4.6 identificado; 2.008 funções detectadas no Ghidra e 1.855 exportadas ao RecompOne.
- Container EA, `.LSC`, `Cpag` e `Ctrk` possuem entendimento útil.
- RAM, velocidade, roster de 168 carros, recursos e grid possuem pontos confirmados.
- RecompOne gera e compila C#; no macOS ARM a janela abre, o jogo entra no `main`, inicializa os
  subsistemas e localiza `CW/OPENING/LEGAL.LSC`.
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
- gates locais para build, checksums, testes, formato e regressão de progresso;
- testes dos parsers e experimentos dinâmicos;
- estrutura e convenções que permitam colaboração paralela.

**Diagnóstico:** a base de *matching decomp* e o primeiro host nativo existem. O bloqueio mais
próximo de algo visível é o fluxo assíncrono de CD após o primeiro `ReadN`. A prioridade passa a
ser intro → menu → corrida original; a decompilação continua como apoio técnico ao port.

## 2. O que os projetos de referência ensinam

| Projeto | Prática que acelera | Aplicação aqui |
|---|---|---|
| [sotn-decomp](https://github.com/Xeeynamo/sotn-decomp) | Splat, configs versionadas, toolchain fixada, diff, permuter, hashes, progresso e CI | Modelo principal do pipeline |
| [silent-hill-decomp](https://github.com/shdecompilations/silent-hill-decomp) | Docker, compiladores/flags por segmento, `include_asm`, objdiff, checksums e convenções | Modelo para identificar toolchain e começar híbrido |
| [mgs_reversing](https://github.com/FoxdieTeam/mgs_reversing) | PsyQ real, Ninja, hash final, métricas por byte/função, variante `dev` e relançamento no PCSX-Redux | Referência mais próxima para build e iteração |
| [ctr-native](https://github.com/CTR-tools/ctr-native) | Separação `game/` × `platform/`, CMake/CTest e replay de bugs | Referência para o port, após uma base C estável |

Não copiar código/layouts de outras engines, complexidade de overlays nem a camada nativa antes da
hora. RecompOne continua útil como laboratório paralelo, mas não mede progresso da decomp.

## 3. Estratégia vigente

1. **Port original (caminho crítico):** RecompOne → primeiro quadro → intro/menu → corrida →
   paridade → pacotes macOS/Windows/Linux.
2. **Matching decomp (trilha de sustentação):** binário → split → build híbrido ASM/C → diff →
   match, priorizando funções que destravem o runtime nativo.
3. **RE e formatos (alimentadora):** Ghidra e experimentos locais esclarecem CD, GPU, SPU, input,
   saves e demais subsistemas necessários à paridade.
4. **Mods e melhorias (congelados):** nenhuma modificação é carregada por padrão. Resolução,
   gráficos e APIs de mod começam somente após uma corrida original completa e estável.

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

### Etapa 5 — Boot original visível — 🟡 EM ANDAMENTO

1. Corrigir a máquina assíncrona de comandos, eventos e interrupções do CD após `Setloc`/`ReadN`.
2. Exibir `OPENING/LEGAL.LSC`, logos, intro e menu sem alterar conteúdo ou comportamento do jogo.
3. Manter carregamento de mods desligado por padrão e tratar erros do host sem gerar falhas do macOS.
4. Registrar traces locais reproduzíveis para cada novo bloqueio, sem enviar CUE/BIN ao GitHub.

**Gate:** o executável macOS ARM chega ao menu, aceita controle e pode ser fechado normalmente.

### Etapa 6 — Primeira corrida original completa

1. Validar input, GPU/MDEC, SPU/música, streaming de CD, física, IA, HUD e transições.
2. Entrar numa corrida a partir do menu, completar voltas e retornar ao frontend.
3. Comparar estados e comportamento observável com a execução de referência, corrigindo o runtime
   em vez de alterar regras ou dados do jogo.

**Gate:** uma corrida completa pode ser jogada do início ao fim sem emulador e sem mods.

### Etapa 7 — Paridade, estabilidade e pacotes

1. Cobrir modos, pistas, carros, power-ups, saves/memory cards e sequências FMV.
2. Eliminar travamentos e dependências de caminhos fixos; permitir selecionar a cópia legal local.
3. Produzir aplicativo macOS e builds Windows/Linux reproduzíveis, sem incluir assets proprietários.
4. Documentar requisitos, controles, logs e diagnóstico por plataforma.

**Gate:** pacotes das plataformas suportadas inicializam a mesma cópia válida e passam pelo menu,
corrida e save com comportamento original estável.

### Etapa 8 — Melhorias e mods após a base original

1. Criar uma chave explícita entre modo original e modo aprimorado/modificado.
2. Implementar resolução, proporção de tela, filtragem e outras melhorias gráficas sem quebrar saves.
3. Retomar editores, SDK de escrita, grid de campeonato e APIs de mods com fixtures e round-trip.
4. Nunca distribuir a imagem ou os assets do jogo; o usuário fornece sua própria cópia legal.

**Gate:** o modo original permanece reproduzível e as melhorias podem ser ativadas separadamente.

## 5. Sprint imediata

1. Impedir exceções não tratadas e manter mods desligados no host padrão.
2. Instrumentar estados, comandos, respostas e IRQs do CD em torno do primeiro `ReadN`.
3. Corrigir o avanço assíncrono até o primeiro quadro da tela legal.
4. Repetir o ciclo para logos/intro até chegar ao menu com input.
5. Somente então atacar a primeira corrida e os subsistemas exigidos por ela.
6. Preservar cada avanço no Git após gates locais; não usar GitHub Actions neste momento.

## 6. Indicadores corretos

- `% bytes .text matched` e `funções matched / total`;
- `% dados matched` por seção e bytes ASM restantes;
- funções nomeadas por confiança e structs com offsets verificados;
- testes, smoke tests e taxa de sucesso;
- último build com checksum idêntico;
- marcos nativos observáveis: janela, primeiro quadro, intro, menu, corrida e save;
- plataformas empacotadas e estáveis, separadas de protótipos apenas compiláveis;
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
| Port mascarar comportamento original | mods desligados; comparar com referência; corrigir runtime |
| Um host funcionar só no Mac do mantenedor | remover caminhos fixos; testar e empacotar por plataforma |
| Regressões silenciosas | checksum, diff por objeto, gates locais e baseline |
| Colaboração difícil | setup de um comando, fila de funções e guia |
| Questões legais | nenhuma ROM/asset; somente hashes, configs, código e fixtures próprias |

## 8. Definição de “chegar ao estágio dos outros”

O primeiro objetivo não é 100%. É obter o mesmo **sistema de produção**:

- build reproduzível verificado por hash;
- fonte híbrida C/ASM sempre executável;
- diff e status por função;
- progresso automático por bytes/funções;
- gates locais e convenções para colaboração;
- port original observável até menu, corrida e save;
- matching, mods e port claramente separados.

Depois disso o avanço passa a ser acumulativo. Como o jogo não possui overlays conhecidos e o EXE
(~638 KiB) é comparável aos executáveis principais já concluídos pelo MGS reversing, a meta é
plausível — mas depende primeiro das Etapas 0–4.
