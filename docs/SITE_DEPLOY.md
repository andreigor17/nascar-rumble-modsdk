# Publicação manual do site

O site é compilado no Mac e publicado na branch `gh-pages`. Não há GitHub Actions nem testes
remotos nesse processo; a branch contém somente os arquivos estáticos produzidos pelo Astro.

Na primeira publicação, execute:

```sh
python3 scripts/deploy_site.py --configure-pages
```

Isso compila `site/`, envia o resultado para `gh-pages` e troca o GitHub Pages de “GitHub Actions”
para “Deploy from a branch”, usando `gh-pages` e `/ (root)`. Nas atualizações seguintes basta:

```sh
make site-deploy
```

O domínio continua sendo `https://rumble.irontech.dev.br`, preservado pelo arquivo `CNAME`.
Nenhum CUE, BIN, executável do jogo ou outro asset proprietário entra na publicação.
