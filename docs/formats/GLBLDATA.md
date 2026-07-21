# `GLBLDATA.PSX` — Dados globais (carros, fontes, objetos)

> ✅ Estrutura mapeada (2026-07-21). Extração: `scripts/extract_resources.py` (resiliente a
> múltiplos containers). Contém os recursos globais do jogo, incluindo os **carros**.

## Estrutura

`GLBLDATA.PSX` (12,3 MB) = **172 containers `CTRL` concatenados** (mesmo padrão do `FE.TRK`),
separados por `FILL`. Cada sub-container agrupa os recursos de uma entidade.

Varredura do arquivo inteiro (1390 recursos com dados):

| Tipo | Qtde | Total | Significado |
|---|---:|---:|---|
| `Cpag` | 171 | 7,7 MB | **Páginas de textura / pinturas dos carros** (liveries) |
| `Cobj` | 693 | 2,9 MB | Modelos/objetos (peças dos carros e cenário) |
| `Ceng` | 171 | 163 KB | Provável **stats/engine por carro** (1 por container) |
| `Cvkb`/`Cvkh` | 1/1 | 181 KB | Corpo/header de veículo (template compartilhado?) |
| `Cfnt` | 6 | 21 KB | **Fontes** do jogo |
| `Csfx`/`Ctos`/`Cshd`/`Cctr` | 1 cada | — | SFX, e diversos globais |
| `SWVR` | 171 | — | Áudio por container (motor de cada carro?) |

## Descobertas

- Os **171 containers "de carro"** têm cada um: 1 `Cpag` (pintura) + `Cobj` (modelo) + `Ceng`
  (stats) + `SWVR` (áudio). Correspondem à grade de carros/pilotos.
- Pinturas confirmadas visualmente: carros de stock car com número, patrocínios e esquemas de
  cor reais — ex.: o **#43 do Richard Petty** (patrocínio EXIDE), pilotos reais da NASCAR.
  (Nas strings do EXE também há `Rick Carelli`, `Golf Cart`, `Jet Car`, `EA Sports Car`.)

## Ferramentas

```bash
python3 scripts/extract_resources.py extracted/GLBLDATA.PSX extracted/glbl_res   # extrai tudo
python3 scripts/decode_cpag.py extracted/glbl_res/cNNN_XXXX_Cpag.bin extracted/glbl_tex  # pintura -> PNG
```

## A fazer

- Mapear qual container = qual carro/piloto (via `Ceng` ou ordem) → catálogo de carros.
- Decodificar `Ceng` (stats) e `Cobj` (malha 3D do carro) → Model Viewer + Car Editor.
