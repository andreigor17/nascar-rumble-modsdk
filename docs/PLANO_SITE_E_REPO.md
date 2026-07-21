# Plano — Repositório GitHub + Site de Apresentação/Devlog

> Objetivo: (1) publicar tudo num repositório Git remoto (nada se perde) e (2) criar um site
> de vitrine + devlog contínuo, inspirado no online-ctr.com, mostrando cada avanço do projeto.

## Decisões tomadas (2026-07-21)

- **Repositório:** privado por enquanto (abrir ao público quando maduro).
- **Site:** Astro · **Idioma:** bilíngue PT/EN · **Hospedagem:** GitHub Pages.
- ⚠️ **Ressalva:** GitHub Pages não publica site de repo **privado** no plano gratuito. Estratégia:
  desenvolver o site agora e mantê-lo "pronto para deploy"; publicar quando o repo for aberto
  (ou via um repo público só do site compilado). O **backup do código** funciona 100% em repo privado.

## Parte 1 — Repositório GitHub (segurança: nada se perde)

Estado atual: repo Git **local** com 8 commits, sem remote. `gh` autenticado como `andreigor17`.

Passos:
1. Criar repositório no GitHub (nome sugerido: **`nascar-rumble-modsdk`**).
2. **Verificação de segurança antes do push** (crítico):
   - Confirmar que a ISO (`*.bin/*.cue`), assets extraídos (`extracted/`), o projeto Ghidra e
     os binários grandes NÃO entram (já cobertos pelo `.gitignore`).
   - O que VAI público: docs, scripts do SDK, CSVs de índice (functions/strings). Isso é padrão
     em projetos de RE (o CTR-ModSDK publica o próprio Ghidra).
3. Adicionar `README.md` (raiz), `LICENSE` (código: MIT) e um `DISCLAIMER` (fan project, sem
   afiliação com a EA, nenhum asset do jogo é distribuído).
4. `git remote add origin …` + `git push`. A partir daí, todo commit sobe (nada se perde).
5. Opcional: proteger `main`, ativar Issues/Discussions para a comunidade.

## Parte 2 — Site de Apresentação + Devlog

### Conceito (o que o online-ctr tem + o que queremos a mais)
- **Landing page** (hero, pitch, estatísticas, screenshots) — como o online-ctr.
- **Devlog/Progresso** — o diferencial: um post por sessão, contando cada passo (é o que você pediu).
- **Documentação** — nossos `docs/` (PRD, plano, formatos, function map) navegáveis.
- **Galeria** — assets que já extraímos (tela LOADING, atlas de textura, traçado da pista).
- **Ferramentas (SDK)** — lista das ferramentas com uso.
- **Roadmap** — as 10 fases com barra de progresso.
- **Sobre/Contribuir** — GitHub, como ajudar, aviso de projeto assistido por IA.

### Estrutura de navegação proposta
```
Início · Progresso (devlog) · Documentação · Galeria · Ferramentas · Roadmap · Sobre
```

### Estatísticas dinâmicas (estilo online-ctr) — geradas do próprio repo no build
- Funções mapeadas: **2008** · Formatos decodificados: **4** (container, LSC, textura, pista)
- Ferramentas do SDK: **7 scripts** · Commits · Sessões registradas

### Fluxo de atualização (como "cada passo" aparece no site)
```
Sessão de trabalho → nota em notes/SESSION_00X.md + docs atualizados
                   → post no devlog → git push → CI reconstrói e publica o site
```
Cada avanço vira automaticamente uma entrada visível no site.

### Tecnologia (a decidir — ver perguntas)
| Opção | Prós | Contras |
|---|---|---|
| **Astro** | Landing bonita + coleções de conteúdo p/ devlog + galeria; rápido; flexível | mais setup inicial |
| **Docusaurus** | Landing + Docs + Blog(devlog) prontos; React; busca | menos "custom" no visual |
| **MkDocs Material** | Menor esforço; ótimo p/ nossos .md; busca nativa; plugin de blog | mais "cara de docs" que de vitrine |

Recomendação: **Astro** (visual de vitrine como o online-ctr + galeria dos assets), com o devlog
em Markdown. Alternativa de menor esforço: Docusaurus.

### Hospedagem (a decidir)
- **GitHub Pages** (tudo no mesmo repo, CI via Actions) — recomendado, simples.
- **Cloudflare Pages** (previews por PR, muito rápido) — alternativa.

### Aviso legal (importante)
- Nenhum asset do jogo é distribuído; a galeria usa **screenshots pequenos** para documentação.
- Disclaimer de "fan project, sem afiliação com a EA"; usuários usam a própria cópia do jogo.

## Entregáveis desta iniciativa
1. Repo no GitHub com push inicial e README/LICENSE/disclaimer.
2. Projeto do site (Astro/Docusaurus) em `site/` dentro do mesmo repo.
3. CI (GitHub Actions) build+deploy automático a cada push.
4. Devlog com as sessões 001–00X já publicadas retroativamente.
5. Galeria inicial (LOADING screen, atlas de textura, traçado JT3).

## Ordem de execução sugerida
1. Decisões (perguntas abaixo). 2. Criar+push do repo GitHub (rápido, garante backup já).
3. Andaime do site + landing. 4. Devlog retroativo (sessões 1–5). 5. CI + deploy. 6. Galeria/Roadmap.
