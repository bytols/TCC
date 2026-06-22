# Slice 3 — Countdown na tela de espera mobile

## Parent

PRD: [auto-start-player-cap.md](auto-start-player-cap.md)

## What to build

Exibir a contagem regressiva de auto-start também na tela `/waiting` dos jogadores mobile. Quando há ≥ 2 jogadores no lobby, a waiting screen passa a mostrar o countdown ("Jogo começa em Xs") abaixo do ícone de TV, substituindo ou complementando "AGUARDE OS JOGADORES".

O mobile **apenas exibe** — nunca chama `/admin/start`. A lógica é a mesma do desktop: escuta `player_joined` e `state_change`, inicia o timer local quando `player_count >= 2`, cancela se cair abaixo de 2 ou ao receber `state_change` com `ROUND_1`.

`AUTO_START_SECONDS` é embutido no template `mobile/waiting.html` via Jinja (mesma abordagem do Slice 2).

## Acceptance criteria

- [ ] `AUTO_START_SECONDS` é passado ao contexto de `mobile/waiting.html` pela rota `/waiting`
- [ ] Com 0 ou 1 jogador no lobby, a waiting screen não exibe countdown (mostra o estado padrão "AGUARDE")
- [ ] Quando `player_count` atinge 2 (via evento WebSocket), o countdown aparece na tela do jogador
- [ ] O countdown não reseta quando novos jogadores entram
- [ ] Ao zerar, a tela do jogador reage ao `state_change` normalmente (já redireciona para `/round/1`)
- [ ] O mobile nunca chama `/admin/start` — a transição de estado vem exclusivamente do desktop

## Blocked by

- [Slice 2 — Countdown auto-start no desktop](slice-2-countdown-desktop.md) — `AUTO_START_SECONDS` precisa estar em `config.py` e a abordagem de passar via template Jinja precisa estar estabelecida.
