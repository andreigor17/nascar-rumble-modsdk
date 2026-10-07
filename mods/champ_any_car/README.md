# Mod `champ_any_car` — qualquer carro como oponente no Championship

**Objetivo:** no Championship o jogo monta o grid sozinho (sem "Select Opponents", que só existe no
Single Race). Este mod injeta a lista de oponentes que você quiser — qualquer piloto, qualquer classe.

Base de RE: `docs/FUNCTION_MAP.md` (seção "Grid de oponentes"), `notes/SESSION_010.md`.

## Alvos (✅ confirmados estático + ao vivo)

| Símbolo | Endereço | Papel |
|---|---|---|
| `grid_build` | `0x8008927c` | monta o grid: contagem + identidades, oponentes sorteados via RNG |
| `grid_spawn` | `0x8003132c` | lê a tabela e instancia os carros na largada |
| `rng_next` | `0x800181ac` | RNG customizado (lagged-Fibonacci); 12 dos 42 usos estão dentro de `grid_build` |
| tabela do grid | `0x800b0e40` | `[+0]` nº de carros; N entradas de **8 bytes** |

Entrada de 8 bytes: `+0` flag (`01`=jogador) · `+1` **tipo** (`0xFF`=IA, `0x00`=jogador) ·
**`+2` MODEL ID** · `+4` ordem de largada.

`MODEL ID = piloto(0..55) + 56 * classe` (0=Rookie, 56=Pro, 112=Elite).

## Estratégia: wrapper pós-`grid_build`

Não reimplementamos a montagem do grid. Deixamos o jogo fazer tudo (contagem, posições,
embaralhamento, pools) e **só reescrevemos o byte `+2`** das entradas de IA:

```
jal grid_build   ──patch──>   jal grid_build_hook
                                   │
                                   ├─ grid_build(mode)    (original, intacto)
                                   └─ reescreve ENT_MODEL(i) dos oponentes
```

**Por que em `grid_build` e não em `grid_spawn`:** `grid_spawn` tem call site único (`0x80029c64`,
1 patch só, tentador) mas roda **depois** do carregamento de recursos. Se injetarmos um carro de
outra classe ali, os `Cpag`/`Cobj` dele podem não estar em memória → carro glitchado/ausente.
`grid_build` roda **antes** do load, então o loader traz as liveries certas.

> 🔬 **A verificar empiricamente** (com `scripts/mod_grid_live.py`): se a injeção tardia
> (pré-`grid_spawn`) já funciona, o mod fica com 1 patch em vez de 4. Testar trocando um oponente
> para outra classe **durante o loading** e ver se a livery aparece correta.

## Pontos de injeção

Patch de **4 palavras** (todas o mesmo valor), trocando o alvo dos `jal grid_build`:

| Endereço | Original | Vira |
|---|---|---|
| `0x8007ae14` | `jal 0x8008927c` (`0x0C02249F`) | `jal grid_build_hook` |
| `0x80081a60` | idem | idem |
| `0x800854d8` | idem | idem |
| `0x80091034` | idem | idem |

Encoding: `jal X` = `0x0C000000 | ((X >> 2) & 0x03FFFFFF)`.
O **delay slot** de cada call site fica intacto — `grid_build` recebe o argumento em `a0`, que é
carregado antes/no delay slot, e nosso hook tem a mesma assinatura `void(char)`, então o
encaminhamento é transparente. *(Conferir o delay slot dos 4 sites antes de fechar o patch.)*

## Onde fica o código do hook — ⚠️ em aberto

O texto do EXE vai de `0x80010000` a `0x800AF800` (`t_size 0x9F800`), **sem overlays** (vantagem
nossa). Mas **não dá para simplesmente anexar depois do texto**: a BSS/heap começa logo acima
(`0x800b0e40`, `0x800b6188`, `0x800b7168` estão todos > `0x800AF800`).

Opções a avaliar:
1. **Padding interno** do EXE (runs de zeros alinhados) — precisa de um scan.
2. **Sobrescrever código morto** (ex.: caminhos de `printf` de debug, que o EXE tem de sobra).
3. Região alta da RAM não usada pelo jogo (verificar ao vivo com o emulador).

O hook é pequeno (~40 instruções), então padding interno deve bastar.

## Arquivos

- `hook.c` — o wrapper. **A lista de oponentes fica em `kOpponents[]`, edite ali.**
- `../../scripts/mod_grid_live.py` — banco de provas: lê/edita o grid ao vivo no PCSX-Redux
  (`show` / `set` / `opponents` / `class`). Valida o conceito sem tocar na ISO.

## Ordem de trabalho

1. ✅ Achar `grid_build` / tabela / layout — feito (sessão 010).
2. ⬜ Provar ao vivo com `mod_grid_live.py` (inclui responder a janela de recursos).
3. ⬜ Achar espaço livre para o código do hook.
4. ⬜ Compilar com `psx-modding-toolchain` (gcc-mipsel) e aplicar os 4 patches.
5. ⬜ Reempacotar com `mkpsxiso` + gerar `xdelta`.
6. ⬜ Espelhar o hook na Trilha B (RecompOne), onde é só um patch no C# gerado.
