# Split e build matching do `SLUS_010.68`

## Resultado

A Etapa 2 produz um ELF intermediário e reconstrói o PS-X EXE de 655.360 bytes com igualdade
byte a byte. Referência e rebuild possuem SHA-256:

```text
e90e3c7e4cf286a7a0a5e827b3a404bfe8407b15f8b2fd54536d426682b20f75
```

O Splat 0.50.0, suas dependências Python e o binutils MIPS 2.47 estão fixados em
`requirements-splat.lock` e `config/splat_toolchain.lock.json`. Os artefatos do jogo e as saídas
geradas permanecem fora do Git.

## Mapa inicial

| Região | Arquivo | VRAM | Tamanho | Evidência |
|---|---:|---:|---:|---|
| Header PS-X EXE | `0x00000` | — | `0x800` | formato do executável |
| Prefixo/padding | `0x00800` | `0x80010000` | `0x30` | primeiro símbolo Ghidra em `0x80010030` |
| Envelope `.text` | `0x00830` | `0x80010030` | `0x99BC4` | 1.855 funções confirmadas; última termina em `0x800A9BF4` |
| `.rodata` inicial | `0x9A3F4` | `0x800A9BF4` | `0x54F0` | fim do último código confirmado |
| `.sdata` inicial | `0x9F8E4` | `0x800AF0E4` | `0x43C` | valor de `gp` instalado pelo startup |
| `.data` final | `0x9FD20` | `0x800AF520` | `0x18` | último dado inicializado antes do BSS |
| `.bss` | sem bytes | `0x800AF538` | `0xD9B0` | loop de limpeza em `0x800A5440` |
| Padding do payload | `0x9FD38` | `0x800AF538` | `0x2C8` | alinhamento do PS-X EXE em `0x800` |

O envelope de texto ainda contém ilhas de dados entre objetos. O Splat as representa sem perda
na montagem integral, inclusive com `.word` quando necessário. Separar objetos e classificar cada
ilha com mais precisão é refinamento incremental; não altera o gate byte a byte.

## Símbolos e `-G`

`scripts/generate_splat_symbols.py` importa todas as 1.855 funções do intervalo carregado a
partir de `ghidra_out/functions.csv`. Símbolos descobertos pelo disassembler continuam nomeados por
endereço.

`scripts/classify_gp_usage.py` registra evidência positiva para o particionamento `-G`: 503
funções possuem instruções relativas a `$gp`; as outras 1.352 ficam explicitamente não
classificadas. Ausência de acesso a `$gp` em uma função não prova que seu objeto original usou
`-G0`. Enquanto o código permanece ASM, seus encodings originais preservam essa distinção.

## Reprodução

Requer Python 3.14 e, no macOS arm64, `mipsel-linux-gnu-binutils` 2.47 do Homebrew:

```sh
make setup
make extract
make build
make check
make test
```

`make setup` instala o lock Python com `--require-hashes`. `make extract` valida a referência,
regenera símbolos/inventário `$gp` e executa o Splat. `make build` monta MIPS I com seções sem
padding implícito e relinka o ELF. `make check` exige a igualdade integral do executável.
