## Mudança

Descreva o que mudou e a evidência usada.

## Progresso

- [ ] `make progress-write` foi executado se o estado matching mudou.
- [ ] O delta de bytes/funções é intencional e não reduz a baseline.
- [ ] Código non-matching está isolado e identificado como tal.

## Validação

- [ ] `make ci-public`
- [ ] `make ci-full` com uma referência legal local, quando a mudança afeta split/build/C
- [ ] Nenhuma ROM, asset, BIOS, savestate ou ferramenta proprietária foi adicionada

Inclua o resultado relevante de `make diff FUNC=...` ou `make objdiff FUNC=...`.
