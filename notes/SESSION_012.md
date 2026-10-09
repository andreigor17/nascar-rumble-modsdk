# Sessão 012 (2026-10-08) — opções de vídeo e continuidade

## Objetivo

Adicionar ao lançador do port nativo opções de resolução, tela cheia e qualidade gráfica,
preservando o aspecto 4:3 do jogo. Manter a investigação de 30/60 fps separada das opções de
vídeo para não misturar apresentação, cadência de VBlank e física.

## Estado encontrado no início

- O lançador já salva `Fps`, `ShowFps` e `Debug` em `launcher.json`.
- A janela do RecompOne nasce fixa em 1280×720.
- O RecompOne já possui fullscreen/F11 e dois modos internos: escala 1× (`NativeResolution`) ou
  4× (padrão), mas essas opções ficam escondidas no menu técnico quando o debug está desligado.
- A saída já preserva o aspecto informado pelo renderizador; a nova interface não deve esticar
  a imagem para 16:9.
- O travamento antigo ao sair da corrida já está corrigido em `NativeHooks.FinishRaceTiming`; não
  faz parte deste pacote.

## Plano desta sessão

1. Acrescentar ao `launcher.json`: modo de tela, resolução, escala interna e filtro de apresentação.
2. Aplicar as preferências salvas antes da criação da janela.
3. Permitir trocar as opções no lançador e aplicá-las antes do boot do jogo, inclusive recriando
   o backend gráfico quando a escala interna mudar.
4. Manter as extensões genéricas do RecompOne no patch canônico
   `recompone/patches/recompone-macos.patch`.
5. Atualizar testes e `docs/LAUNCHER.md`, compilar e validar o patch contra um checkout limpo.

## Registro de andamento

- Início: confirmado que o worktree principal só tinha `.claude/` não versionado; ele pertence ao
  mantenedor e não será alterado.
- Confirmado que `tools/RecompOne` está no commit fixado
  `4edc6899a4516f292facfd35b77a2fd2d79e03c1` e que o patch canônico atual pode ser revertido
  integralmente (`git apply --reverse --check`).

## Resultado

Concluído. O lançador agora oferece modo de tela, resolução, qualidade gráfica e filtro de
apresentação, além das opções já existentes de frame rate, contador de FPS e debug. As escolhas
são normalizadas, salvas em `launcher.json` e aplicadas antes do boot; a janela continua exibindo
o jogo em 4:3.

Arquivos alterados:

- `recompone/host/Launcher.cs`
- `recompone/host/Program.cs`
- `recompone/patches/recompone-macos.patch`
- `tests/test_native.py`
- `docs/LAUNCHER.md`

Validação executada:

- `python3 -m unittest tests.test_native -v`: 11 testes aprovados.
- `make test-public`: 29 testes executados, 26 aprovados e 3 pulados conforme esperado.
- `make native-build`: compilação concluída sem erros; os 53 avisos são de código gerado
  inalcançável já conhecido.
- `make format-check`, `make lint-config` e `git diff --check`: aprovados.
- Patch aplicado em clone limpo do RecompOne no commit fixado
  `4edc6899a4516f292facfd35b77a2fd2d79e03c1`: zero divergências nos 15 fontes alterados.
- Inspeção visual local: janela 1280×720, quadro 4:3 preservado e as nove linhas do menu visíveis,
  legíveis e sem sobreposição. O processo foi encerrado sem confirmar o menu, portanto a inspeção
  não salvou preferências.

Próximo passo: teste manual dos ciclos de fullscreen e das três escalas internas durante uma
sessão de jogo; isso é validação de plataforma, não bloqueio para integrar este pacote.
