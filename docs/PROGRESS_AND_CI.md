# Métricas, validação local e governança

`progress.json` é a fonte canônica de progresso da decompilação. Ele é gerado de forma
determinística por `scripts/progress.py` a partir de `config/function_backlog.csv`, dos objetos C
registrados, dos símbolos e dos limites de seção. README e site apenas consomem esse arquivo.

## Significado das métricas

- **Código matched:** bytes pertencentes a funções detectadas que foram substituídas por C e
  continuam idênticas no executável final. O denominador não inclui as ilhas ainda não
  classificadas dentro do envelope inicial de `.text`.
- **Funções matched:** funções C com status `matched`; funções apenas detectadas ou nomeadas não
  contam.
- **Dados matched:** bytes inicializados de `.rodata`, `.sdata` e `.data` reconstruídos exatamente.
  Hoje estão em ASM; 100% aqui significa reconstrução, não entendimento ou tipagem dos dados.
- **ASM restante:** bytes de funções detectadas que ainda não foram substituídas por C matching.
- **Símbolos:** total importado e divisão entre nomes por endereço (`FUN_...`) e nomes descritivos.
  “Descritivo” não substitui uma classificação de confiança.
- **Subsistemas:** cobertura somente de grupos explicitamente atribuídos em
  `config/progress_config.json`. O restante aparece como `unclassified`, sem inferência inventada.

Comandos:

```sh
make progress          # resumo legível e próximas funções folha
make progress-write    # atualiza progress.json após uma mudança matching
make progress-check    # detecta manifesto obsoleto e regressão
```

`config/progress_baseline.json` define mínimos que só podem subir e o máximo de ASM que só pode
cair. Uma mudança de fronteiras pode alterar denominadores, mas precisa de justificativa explícita
e de um rebuild byte a byte antes de atualizar a baseline.

## Gates locais antes do Git

Por decisão do mantenedor, a cópia legal do jogo permanece somente no Mac. Não há workflows do
GitHub Actions nem bundle privado. O GitHub é usado somente para versionar o código, sem receber
BIN, CUE ou EXE.

Antes de cada push:

```sh
make ci-public
```

Quando a alteração tocar no split, linker, ASM ou C matching:

```sh
make ci-full
```

O segundo comando verifica a referência local, refaz o split e exige que o executável reconstruído
tenha SHA-256 `e90e3c7e4cf286a7a0a5e827b3a404bfe8407b15f8b2fd54536d426682b20f75`.

A imagem `matching-ci` compila binutils 2.47 do tarball upstream cujo SHA-256 está fixado. Python
3.14.0 e Rust 1.74.1 também usam imagens fixadas por digest; Rust existe apenas no estágio que
compila as extensões Python e não entra na imagem final. As dependências Python e as ferramentas
de decomp ficam em camadas separadas do código, permitindo que mudanças normais reutilizem o cache.
Splat, MASPSX, PsyQ, Wibo e objdiff são baixados somente das versões/commits e checksums versionados. No
macOS o mesmo compilador Windows é executado por Wibo; Wine não é necessário. `make
docker-matching` força `linux/amd64`, inclusive em Apple Silicon, para usar o binário Wibo
versionado e reproduzir a arquitetura do runner hospedado pelo GitHub. Com Colima em Apple
Silicon, use um perfil de VM completo `--arch x86_64 --vm-type qemu`: Rosetta não executa o
compilador Windows de 32 bits dentro do Wibo, e QEMU/binfmt também não é estável nessa combinação.

Validação local de 2026-10-07: `make docker-matching` passou em um perfil Colima x86-64/QEMU e
`make ci-full` reconstruiu `SLUS_010.68` com SHA-256
`e90e3c7e4cf286a7a0a5e827b3a404bfe8407b15f8b2fd54536d426682b20f75`. As referências foram
montadas como somente leitura e não entraram no contexto nem na imagem Docker.

O site já publicado permanece disponível, mas não recebe deploy automático enquanto essa política
estiver vigente.
