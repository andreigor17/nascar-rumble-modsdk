# Contribuindo

Obrigado por ajudar a transformar a pesquisa em uma decompilação reproduzível. O repositório não
distribui o jogo, BIOS, savestates, assets extraídos nem executáveis proprietários. Use somente uma
cópia legal de `SLUS_010.68` com os hashes de `config/reference_hashes.json`.

## Setup

No macOS, instale `mipsel-linux-gnu-binutils`; Wibo executa a toolchain PsyQ fixada. No Linux, a
imagem Docker contém Python, Make e binutils MIPS; um estágio Rust fixado por digest compila as
extensões Python e não entra na imagem final. `make setup` baixa as ferramentas versionadas e
confere seus SHA-256:

```sh
make setup
make extract
make build
make check
make test
```

Docker Desktop em host amd64 funciona diretamente. Em Mac Apple Silicon com Colima, o gate
matching precisa de uma VM x86-64 completa: Rosetta executa o toolchain Linux, mas não o
compilador Windows de 32 bits dentro do Wibo; QEMU/binfmt também não suporta essa combinação com
estabilidade. Crie um perfil separado:

```sh
brew install docker docker-buildx colima qemu lima-additional-guestagents
colima start rumble-amd64 --arch x86_64 --vm-type qemu \
  --cpu 2 --memory 3 --disk 10 --mount "$PWD:w"
make docker-matching
```

Para executar os gates públicos localmente, sem arquivos do jogo:

```sh
make docker-public
```

Com os três arquivos legais de referência nos caminhos descritos abaixo, reproduza também o gate
matching. Esse alvo usa `linux/amd64`, pois o Wibo fixado é x86-64:

```sh
make docker-matching
```

## Uma função por mudança

1. Escolha uma função `asm` em `config/function_backlog.csv` e registre responsável/scratch.
2. Gere o contexto com `make context FUNC=...`.
3. Coloque o C em `src/<subsistema>/`, registre o objeto e o subsistema em `config/`.
4. Use `make diff FUNC=...` e `make objdiff FUNC=...` até obter 100%.
5. Rode `make ci-full`, depois `make backlog` e `make progress-write`.
6. Revise o delta local de progresso e descreva-o no commit ou PR.

Preserve nomes baseados em endereço até existir evidência para um nome semântico. Tipos e offsets
devem citar uma análise, acesso observado ou teste; não promova uma hipótese silenciosamente.

## Política matching e non-matching

O split principal aceita C apenas quando o objeto e o executável final continuam idênticos à
referência. Código semanticamente correto, mas non-matching, deve ficar fora do split principal,
com status explícito, motivo e scratch reproduzível. Experimentos e variantes de mod ficam em
`experiments/` ou `mods/`; nunca alteram a métrica matching.

`progress.json` é gerado por `scripts/progress.py`. Não edite percentuais no README ou no site.
Uma redução de bytes/funções matched, dados reconstruídos ou símbolos, ou um aumento de ASM,
falha contra `config/progress_baseline.json`. Atualizar a baseline para aceitar regressão exige
justificativa explícita e revisão; avanço normal só eleva os mínimos e reduz o máximo de ASM.

## Formato e testes

`make ci-public` valida JSON/Splat, sintaxe/formato de Python e C, testes sem ROM, o manifesto de
progresso e a baseline. Mudanças no build também exigem `make ci-full`, que executa split, build,
SHA-256, testes e os gates das etapas anteriores. Dependências novas precisam de versão/commit e
checksum; downloads sem pin não entram no pipeline.
