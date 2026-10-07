# Compiler probe

Corpus mínimo usado para identificar a versão e as flags do compilador original. O arquivo C
representa padrões observados em funções pequenas do jogo; as saídas geradas ficam em `build/` e
não devem ser tratadas como fonte.

Referências iniciais:

| Probe | Função observada |
|---|---|
| `probe_empty` | `0x8001930c`, entre outras |
| `probe_store_zero` | `0x8001adb4` |
| `probe_return_7096` | `0x8001f3bc` |
| `probe_return_one` | `0x80022878` |
| `probe_clear_byte_1` | `0x800401cc` |
| `probe_clear_byte_1012` | `0x80059a48` |
| `probe_set_byte_26_to_3` | `0x80072dc8` |
| `probe_set_byte_26_to_9` | `0x800734f4` |
| `probe_init_fields` | `0x80071dd4` |
| `probe_scaled_byte` | `0x80044158` |
| `probe_clamp_between` | `0x8008aad8` |
| `probe_min` | `0x80097cf4` |

O corpus versionado em `config/compiler_corpus.json` possui 23 funções e cobre branches,
aritmética, listas, structs, globals e índices. Este arquivo contém somente os probes já escritos;
os casos com `gp`, chamadas e stack são o próximo lote.
