# Toolchain matching validada

## Resultado

A baseline de compilação do código próprio é:

- `cc1psx` da distribuição PsyQ 4.3 — **GNU C 2.7.2.SN32.3.7 Build 0001**;
- `-O2 -G0 -g0` para o módulo discriminador validado;
- ASPSX 2.56;
- PSYLINK 2.73.

Os hashes e a origem estão fixados em `config/toolchain.lock.json`. Os binários não são
versionados neste repositório.

## Evidência

1. Dez funções próprias pequenas produzem bytes idênticos em PsyQ 4.3 e 4.4 com `-O2`; elas
   confirmam família/otimização, mas isoladamente não distinguem a revisão.
2. `FUN_80078c24` (`0x80078c24`, 36 bytes) contém prólogo, chamada externa e epílogo:
   - PsyQ 4.3: **36/36 bytes idênticos**;
   - PsyQ 4.4: diferente no agendamento do delay slot do epílogo.
3. A matriz `O1/O2 × G0/G8` obteve 9/12 matches com O1 e 10/12 com O2 no corpus sem globals,
   confirmando `-O2`. O `G` não pode ser distinguido por funções que não acessam small data.
4. O jogo contém tanto acessos absolutos quanto acessos relativos a `gp`; `-G` deve ser classificado
   por módulo/objeto durante o split, não imposto globalmente.
5. PSYLINK relinkou o módulo de probes em `0x80010000` duas vezes com CPE byte-idêntico:
   `3617f0369cb3469593d9dc375979eb21d8d3d2138faaf60e54ccf58ef54bce21`.

## Reprodução

```sh
python3 scripts/compiler_probe.py --matrix \
  --sdk-root /caminho/psyq_sdk \
  --wibo /caminho/wibo-macos
```

O comando falha se um match obrigatório regredir, se PsyQ 4.3 deixar de reproduzir o probe
discriminador, se 4.4 passar indevidamente ou se o relink deixar de ser determinístico.

## Limites conhecidos

- A identificação de PsyQ 4.6 em strings/bibliotecas do jogo não implica que o C tenha sido
  compilado pelo `cc1psx` distribuído naquele SDK; a evidência de código aponta para o compilador
  PsyQ 4.3 acima.
- Dois probes C exploratórios ainda não reproduzem a ordenação de registradores/branches. Isso é
  trabalho normal de matching por função e não invalida a identificação da toolchain.
- O split futuro deve detectar fronteiras de objetos e seus respectivos `-G0/-G8`.
