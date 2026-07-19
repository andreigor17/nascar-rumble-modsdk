# Roteiro de Setup — Toolchain e Primeiro Import no Ghidra

> Alvo: macOS **Apple Silicon (arm64)**. Ambiente já verificado: Homebrew ✅, Java 21 ✅,
> Python 3.9 ✅, Git ✅, ~30 GB livres. Versões travadas e compatíveis (ver Parte B).
> Princípio do PRD: trabalhar sempre sobre cópias extraídas, nunca na ISO.

## Ordem recomendada

1. **Parte A — dependências Python** (1 min, já dá pra usar as ferramentas do SDK).
2. **Parte B — Ghidra + ghidra_psx_ldr** (prioridade: é o caminho para destravar o container e a física).
3. **Parte C — Emuladores** (DuckStation para jogar/testar; PCSX-Redux para debug/RAM).

---

## Parte A — Dependências Python

```bash
cd /opt/Projetos/rumble
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install kaitaistruct pillow numpy
```

- `kaitaistruct` — runtime das especificações de formato (`docs/formats/*.ksy`).
- `pillow` — salvar/visualizar texturas e as telas `.LSC` quando decodificarmos.
- `numpy` — análise de blobs (entropia, busca de padrões, geometria).

> As ferramentas `scripts/iso_tree.py` e `scripts/chunk_explorer.py` já rodam só com a stdlib.

---

## Parte B — Ghidra 12.1.2 + extensão PSX (o caminho principal)

### B.1 Instalar o Ghidra

```bash
brew install ghidra          # instala a 12.1.2 (usa o Java 21 já presente)
ghidra --version 2>/dev/null || echo "use o comando 'ghidra' para abrir"
```

### B.2 Instalar a extensão ghidra_psx_ldr (carrega PS-X EXE + mapa de memória PS1)

A extensão é **travada por versão**. Existe um build exatamente para a 12.1.2 — não pegar outro.

```bash
cd "$(mktemp -d)"
curl -L -o psxldr.zip \
  https://github.com/lab313ru/ghidra_psx_ldr/releases/download/2026.07.08/ghidra_12.1.2_PUBLIC_20260709_ghidra_psx_ldr.zip
echo "Baixado em: $(pwd)/psxldr.zip"
```

Depois, dentro do Ghidra (GUI):

1. Abra o Ghidra: `ghidra`
2. Menu **File → Install Extensions…**
3. Clique no **+** (canto superior direito), selecione o `psxldr.zip` baixado.
4. Marque a extensão na lista, **OK**, e **reinicie o Ghidra**.
5. Confirmação: ao reimportar um PS-X EXE, o loader **"PSX executable (PS-X EXE)"** aparece
   na lista de formatos. Se aparecer, a extensão está ativa. ✅

> Se o download 404: rode `curl -s https://api.github.com/repos/lab313ru/ghidra_psx_ldr/releases/latest | grep 12.1.2`
> para pegar o nome atual do asset da sua versão do Ghidra.

### B.3 Roteiro do PRIMEIRO import — `SLUS_010.68`

**Objetivo:** ter o executável desmontado, com o mapa de memória do PS1 aplicado, pronto para
localizar (a) o parser do container CTRL/SHOC e (b) as tabelas de física/power-ups.

**Por que importa:** o executável é a única fonte que dá a *semântica* dos bytes que já mapeamos
(os 8 bytes de prefixo do SHOC, se o SDAT é comprimido, o layout das structs em RAM).

Passo a passo:

1. **Novo projeto:** File → New Project → *Non-Shared* → salvar em `/opt/Projetos/rumble/ghidra/`,
   nome `NASCAR_Rumble`.
2. **Importar:** File → Import File → `/opt/Projetos/rumble/extracted/SLUS_010.68`.
   - Formato: **PSX executable (PS-X EXE)** (o loader detecta sozinho).
   - Opção de RAM: **2 MB** (NASCAR Rumble é PS1 retail, sem expansão).
   - O loader lê o cabeçalho e posiciona o código em **0x80010000**, entry point **0x800A5440**.
3. **Auto-análise:** ao abrir no CodeBrowser, aceite rodar os analisadores. Mantenha os padrões
   + os específicos de MIPS/PSX. (Pode levar alguns minutos.)
4. **Aplicar assinaturas PsyQ (se disponível):** Analysis → *Function ID* / *Apply Signatures*.
   Isso nomeia funções da biblioteca da Sony (libgpu, libspu, libcd) e economiza semanas.

### B.4 O que fazer logo após a análise (checklist do FUNCTION_MAP)

- **Window → Defined Strings:** procure `".TRK"`, `".LSC"`, `"GLBLDATA"`, mensagens de debug.
  Cada string com referência (duplo-clique → *References*) leva a uma função de alto nível.
- **Atalho para a "pedra de roseta"** (achar o parser do container):
  - Search → For Scalars → valor **`0x4354524C`** (é `"LRTC"`/CTRL lido como u32 little-endian).
  - A instrução que compara a tag com esse imediato **é o parser dos chunks**. Renomeie a função
    para `parse_ea_chunk` e documente os campos. Isso resolve os 8 bytes misteriosos do SHOC.
- Localize o **loader de arquivos de CD** (referências a libcd / `CdReadFile`) — quem lê `GLBLDATA.PSX`.
- Exporte o progresso: File → Export Program → **Ghidra Zip File (.gzf)** em `ghidra/` (versionável).
- Anote tudo em `docs/FUNCTION_MAP.md` (endereço, nome, papel, evidência, classificação ✅🟡🔵❓).

---

## Parte C — Emuladores

Nenhum tem cask no Homebrew; baixamos os builds oficiais.

### C.1 DuckStation (jogar, testar mods, savestates)

```bash
cd ~/Downloads
curl -L -o duckstation-mac.zip \
  https://github.com/stenzek/duckstation/releases/download/latest/duckstation-mac-release.zip
unzip -o duckstation-mac.zip -d duckstation-app
# Arraste o DuckStation.app para /Applications e libere no Gatekeeper:
xattr -dr com.apple.quarantine "duckstation-app/DuckStation.app" 2>/dev/null || true
```

### C.2 PCSX-Redux (debugger — breakpoints, memória, Lua) — para as Fases 4/5/8

Baixe o build de macOS pela página oficial (distribuem por CI, não por release fixo):
- https://pcsx-redux.consoledev.net/  → seção **Install / Getting Started** → macOS.
- É o emulador com o melhor debugger para PS1 e scripting Lua (essencial para o `RAM_MAP.md`).

### C.3 BIOS do PS1 (importante)

- Os emuladores rodam melhor com uma **BIOS real do PS1** (ex.: `SCPH-1001.bin`), que você deve
  **dumpar do seu próprio console** (questão legal — não distribuímos BIOS).
- O DuckStation tem uma BIOS aberta de fallback, mas a real dá maior compatibilidade.
- Coloque a BIOS na pasta que o emulador indicar em *Settings → BIOS*.

### C.4 Primeiro boot

- Abra o DuckStation → *Settings → BIOS* (aponte a BIOS) → arraste o
  `NASCAR Rumble (USA)/NASCAR Rumble (USA).cue` para a janela → o jogo deve iniciar.
- Crie um **Memory Card** virtual (Settings → Memory Cards) — vamos usá-lo na Fase 6 (save editor).

---

## Critério de conclusão desta etapa

- [ ] `.venv` criado com kaitai/pillow/numpy.
- [ ] Ghidra 12.1.2 abre; extensão PSX instalada (loader "PS-X EXE" aparece).
- [ ] `SLUS_010.68` importado e analisado; projeto salvo em `ghidra/NASCAR_Rumble`.
- [ ] Pelo menos 1 função relevante nomeada (idealmente `parse_ea_chunk` via o scalar `0x4354524C`).
- [ ] DuckStation roda o jogo a partir do `.cue`.
- [ ] `docs/FUNCTION_MAP.md` iniciado.

Ao concluir, me traga: (1) print da Defined Strings com os nomes de arquivo, e (2) a função
encontrada pelo scalar `0x4354524C`. A partir daí eu interpreto e definimos o próximo passo.
