# Slice 2 — Countdown auto-start no desktop

## Parent

PRD: [auto-start-player-cap.md](auto-start-player-cap.md)

## What to build

Implementar o auto-start de 30 segundos visível na tela da TV (desktop). Quando o 2º jogador entra no lobby, o desktop exibe uma contagem regressiva ("Começando em Xs") e ao zerar chama `POST /admin/start` automaticamente, iniciando o jogo sem intervenção do host.

O botão INICIAR permanece como atalho: se clicado durante o countdown, inicia imediatamente.

O countdown é inteiramente client-side: o desktop JS escuta os eventos WebSocket `player_joined` e `state_change`, inicia o timer local quando `player_count >= 2`, e o cancela se `player_count` cair abaixo de 2 ou se o estado mudar para `ROUND_1` (via INICIAR manual ou outro cliente).

A duração do countdown é configurável via variável de ambiente `AUTO_START_SECONDS` (padrão: 30). O valor chega ao frontend embutido no template Jinja da lobby como variável JS global.

## Acceptance criteria

- [ ] `AUTO_START_SECONDS` está declarado em `config.py` com padrão 30, lido do ambiente via `os.environ.get`
- [ ] `AUTO_START_SECONDS` está documentado em `.env.example`
- [ ] O valor é exposto ao JS do desktop via variável global no template da lobby
- [ ] Com 0 ou 1 jogador no lobby, nenhum countdown aparece
- [ ] Quando o 2º jogador entra, o desktop exibe a contagem regressiva visível
- [ ] O countdown não reseta quando um 3º ou 4º jogador entra
- [ ] Ao zerar, o desktop chama `POST /admin/start` e o jogo passa para `ROUND_1`
- [ ] Se o host clicar em INICIAR durante o countdown, o jogo inicia imediatamente
- [ ] O countdown para (sem crashar) se `player_count` cair abaixo de 2 via evento WebSocket

## Blocked by

None — can start immediately (parallel com Slice 1).
