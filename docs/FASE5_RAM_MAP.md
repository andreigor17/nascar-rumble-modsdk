# Fase 5 — Mapa de RAM (RAM_MAP.md) via PCSX-Redux

> Objetivo: localizar as **estruturas vivas** do jogo na memória (posição/velocidade do carro,
> volta, timer, carro carregado, IA/power-ups) por *memory diffing*, e registrar em `docs/RAM_MAP.md`.
> Isso destrava a pesquisa de gameplay (Fase 8), o Memory Inspector e o mapeamento roster→livery.

## Por que PCSX-Redux (e não DuckStation)

O PCSX-Redux tem **Lua scripting** e um **Web Server (API HTTP)** que permite **ler/escrever a
memória do jogo por fora**. Ou seja: você joga, e eu leio a RAM e faço o diffing do meu lado.
Além disso traz o **OpenBIOS** embutido — roda o jogo **sem precisar de BIOS real**.

## Passo 1 — Instalar e rodar (você)

1. Baixe o PCSX-Redux para macOS (Apple Silicon) no site oficial:
   **https://pcsx-redux.consoledev.net/** → seção *Getting Started / Install* → build de macOS.
   (Descompacte e arraste `PCSX-Redux.app` para `/Applications`. Se o Gatekeeper reclamar:
   `xattr -dr com.apple.quarantine /Applications/PCSX-Redux.app`.)
2. Abra o PCSX-Redux. Se pedir BIOS, escolha usar o **OpenBIOS** (Configuration → BIOS).
3. Carregue o jogo: **File → Open ISO** (ou *Open Disk Image*) apontando para
   `NASCAR Rumble (USA)/NASCAR Rumble (USA).cue`. O jogo deve iniciar.

## Passo 2 — Ligar o Web Server (para eu ler a memória)

- Menu **Configuration → Emulation** (ou *Settings*): habilite **"Enable Web Server"**.
  Porta padrão **8080**. (Se houver campo de porta, deixe 8080.)
- Confirme que ficou ativo: com o jogo aberto, eu testo `http://localhost:8080/` do meu lado.

> Alternativa (se o Web Server não expuser leitura de memória na sua versão): uso a **console Lua**
> (menu *Debug → Lua console*) com um script que eu forneço para despejar a RAM num arquivo — e eu
> leio o arquivo. Decidimos qual caminho após ver a sua versão.

## Passo 3 — Memory diffing (juntos)

Técnica clássica de "cheat search":
1. Escolhemos um valor observável (ex.: **contador de voltas**, **velocidade**, **timer**).
2. Você deixa o jogo num estado A; eu tiro um retrato da RAM.
3. Você muda o valor (dá uma volta, acelera); eu tiro o retrato B.
4. Eu **diffo** A×B e vou estreitando até 1 endereço. Repetimos para cada variável.
5. Cada endereço confirmado entra em `docs/RAM_MAP.md` com evidência.

Alvos iniciais (ordem sugerida):
- Contador de voltas e posição na corrida (fáceis, mudam em passos discretos).
- Velocidade e posição (X,Y,Z) do carro do jogador.
- A partir da struct do jogador, achar o **array de carros da IA** (mesmo layout, offsets seguidos).
- Índice do carro carregado (fecha o mapeamento **roster→livery** que ficou pendente).

## Entregável

`docs/RAM_MAP.md` com os endereços confirmados (nome, endereço, tipo, evidência, classificação
✅🟡🔵). Base do **Memory Inspector** e do futuro **Save Editor**.

## Primeiro passo concreto

Instalar o PCSX-Redux, rodar o NASCAR Rumble e ligar o Web Server. Quando estiver rodando, me avise
que eu verifico a conexão e a leitura de memória, e começamos o diffing pelo contador de voltas.
