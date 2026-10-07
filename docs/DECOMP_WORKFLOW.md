# Fluxo por função

A Etapa 3 transforma uma função do backlog em C integrado sem depender de abrir o projeto Ghidra.
As ferramentas, versões e checksums estão em `config/decomp_tools.lock.json`; `make setup` instala
Splat, asm-differ, MASPSX, PsyQ 4.3, Wibo e objdiff.

## Ciclo mínimo

```sh
make setup
make extract
make build

make context FUNC=FUN_80078c24
make diff FUNC=FUN_80078c24
make objdiff FUNC=FUN_80078c24
make progress
make check
```

`make context` cria em `scratch/<FUNÇÃO>/`:

- `context.c`: endereço, tamanho, callers, callees, strings e decompilação local, quando disponível;
- `target.s`: disassembly pronto para consulta;
- `target.bin`: bytes originais exatos;
- `metadata.json`: os mesmos fatos em formato estruturado.

O diretório `scratch/` é local e ignorado pelo Git. Ele pode ser usado diretamente para trabalhar
ou copiar o contexto para decomp.me. Não há upload implícito nem dependência de uma sessão do
Ghidra: se a exportação grande `decomp_all.c` não existir, bytes, assembly, grafo e strings ainda
são gerados normalmente a partir dos índices versionados e da cópia legal do EXE.

`make diff` compara referência e rebuild ligados e para no primeiro retorno. `make objdiff` cria
um objeto-alvo local, preserva relocações de chamadas conhecidas e grava o relatório completo em
`scratch/<FUNÇÃO>/objdiff.json`. O resultado ligado e o checksum final continuam sendo a autoridade
para declarar um match.

## Backlog

`make backlog` regenera `config/function_backlog.csv` a partir do EXE e das exportações versionadas.
Cada linha contém endereço, tamanho, instruções, callers, callees, strings, uso confirmado de `$gp`,
status, responsável e scratch. Os três últimos campos de fluxo são preservados ao regenerar o CSV.

Estados usados inicialmente:

- `asm`: ainda representada pelo split em assembly;
- `matched`: fonte C integrada e executável final idêntico;
- `nonmatching`: reservado para trabalho correto semanticamente que ainda não pode entrar no build
  matching.

Escolha preferencialmente folhas/utilitários de 20–150 instruções listados por `make progress`.
Uma função só muda para `matched` depois de `make build && make check`; proximidade visual ou
percentual isolado do objdiff não basta.

## Primeiro match integrado

`FUN_80078c24` (`0x80078C24`, 36 bytes) é a prova do ciclo completo. Ela compila com GNU C
2.7.2.SN32.3.7 do PsyQ 4.3, `-O2 -G0 -g0`, passa em 100% no objdiff e mantém o executável de
655.360 bytes com SHA-256
`e90e3c7e4cf286a7a0a5e827b3a404bfe8407b15f8b2fd54536d426682b20f75`.
