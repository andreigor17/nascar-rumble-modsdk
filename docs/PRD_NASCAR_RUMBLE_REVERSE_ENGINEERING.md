# PRD --- Projeto de Engenharia Reversa e SDK de Modding do NASCAR Rumble (PS1)

## Visão

O objetivo deste projeto é compreender completamente o funcionamento
interno do jogo **NASCAR Rumble**, lançado para PlayStation 1,
documentando toda a sua arquitetura e desenvolvendo um SDK de modding
open source que permita criar mods, editar recursos do jogo e,
futuramente, possibilite uma decompilação completa e até um port para
PC, semelhante ao que foi realizado pelo projeto CTR-ModSDK.

Este é um projeto de longo prazo, com duração estimada de meses ou anos.
O foco principal não é modificar o jogo imediatamente, mas sim
entendê-lo profundamente.

## Objetivos Gerais

-   Engenharia reversa do executável principal.
-   Documentação completa dos formatos de arquivos.
-   Ferramentas para extração e edição dos recursos.
-   Editor de texturas.
-   Editor de carros.
-   Editor de pistas.
-   Editor de campeonatos.
-   Editor de saves.
-   Documentação da memória RAM.
-   Documentação das funções do executável.
-   Base de conhecimento aberta para a comunidade.
-   Estrutura preparada para uma futura decompilação "matching".

## Princípios do Projeto

1.  Compreender antes de modificar.
2.  Toda descoberta deve ser documentada.
3.  Todo experimento deve ser reproduzível.
4.  Nunca trabalhar diretamente na ISO original.
5.  Nunca assumir informações sem evidências.

## Papel do Claude Code

O Claude atuará como líder técnico, mentor e especialista em engenharia
reversa.

Fluxo obrigatório para cada tarefa:

1.  Explicar o objetivo.
2.  Explicar por que a etapa é importante.
3.  Fornecer instruções detalhadas.
4.  Aguardar resultados.
5.  Interpretar os resultados.
6.  Definir o próximo passo.

## Frentes de Trabalho

### Frente A --- Engenharia Reversa

-   Análise do executável
-   Assembly MIPS
-   Ghidra
-   Física
-   IA
-   Colisão
-   Renderização
-   Áudio
-   Menus
-   Sistema de save
-   Carregamento de recursos

### Frente B --- SDK de Modding

Ferramentas previstas:

-   ISO Explorer
-   Archive Extractor
-   Texture Viewer
-   Texture Editor
-   Model Viewer
-   Model Exporter
-   Track Viewer
-   Track Editor
-   Car Editor
-   Save Editor
-   Patch Builder
-   Memory Inspector

### Frente C --- Base de Conhecimento

Toda descoberta deve gerar documentação contendo:

-   Diagramas
-   Capturas do Ghidra
-   Mapas de memória
-   Formatos de arquivos
-   Hipóteses
-   Experimentos
-   Resultados
-   Decisões técnicas

## Estrutura do Repositório

``` text
nascar-rumble-sdk/
    docs/
    ghidra/
    tools/
    extracted/
    scripts/
    emulator/
    experiments/
    saves/
    notes/
```

## Roadmap

### Fase 1

Preparação do ambiente (Ghidra, DuckStation, no\$psx, Git, Python, 010
Editor, Kaitai Struct).

### Fase 2

Pesquisa da ISO e geração do `ISO_TREE.md`.

### Fase 3

Desenvolvimento do ISO Explorer.

### Fase 4

Análise do executável e geração do `FUNCTION_MAP.md`.

### Fase 5

Mapeamento da memória e geração do `RAM_MAP.md`.

### Fase 6

Documentação dos formatos de arquivos.

### Fase 7

Expansão do SDK (visualizadores e editores).

### Fase 8

Pesquisa da jogabilidade (física, IA, power-ups, HUD).

### Fase 9

SDK avançado (edição completa e reconstrução de ISOs).

### Fase 10

Pesquisa sobre decompilação matching e port para PC.

## Fluxo de Engenharia Reversa

Observar → Criar hipótese → Planejar experimento → Executar → Validar →
Documentar → Registrar no Git

## Classificação das Descobertas

-   ✅ Confirmado
-   🟡 Provável
-   🔵 Hipótese
-   ❓ Desconhecido

## Critérios de Sucesso

1.  ISO documentada.
2.  SDK inicial funcional.
3.  Recursos extraíveis.
4.  Modelos e pistas editáveis.
5.  Gameplay modificável.
6.  Projeto comparável ao CTR-ModSDK.

## Diretrizes para o Claude

-   Nunca pular etapas.
-   Sempre propor o menor próximo passo possível.
-   Trabalhar orientado por evidências.
-   Manter documentação sincronizada com o código.
-   Sugerir novas ferramentas quando apropriado.
-   Encerrar cada sessão com resumo e próximos passos.
