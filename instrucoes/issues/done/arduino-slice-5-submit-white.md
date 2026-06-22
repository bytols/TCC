# Slice 5 — Confirmação de voto: WHITE ao submeter

## Parent

[PRD: Integração Arduino — Totens LED por Jogador](arduino-led-totems.md)

## What to build

Quando um player registra seus votos em qualquer rodada (rounds 1, 2 ou 3), o totem dele deve acender imediatamente em branco, confirmando fisicamente que a seleção foi registrada — independente do que os outros totens estejam mostrando no momento.

O comando deve ser enviado após a persistência dos votos no banco e antes do redirect, tanto nos casos em que a rodada ainda não fechou quanto no caso em que esse foi o último vote e a rodada encerrou.

## Acceptance criteria

- [ ] `POST /round/1/submit` bem-sucedido → `arduino.send_led(player.id, "WHITE")` é chamado.
- [ ] `POST /round/2/submit` bem-sucedido → `arduino.send_led(player.id, "WHITE")` é chamado.
- [ ] `POST /round/3/submit` bem-sucedido → `arduino.send_led(player.id, "WHITE")` é chamado.
- [ ] Submit que falha por validação (quantidade errada de filmes, voto duplicado) → `send_led` não é chamado.
- [ ] Teste de integração para cada uma das três rotas de submit: `send_led` chamado com `(player_id, "WHITE")`, usando `patch("arduino.send_led")`.

## Blocked by

- [Slice 1 — Módulo `arduino.py`](arduino-slice-1-foundation.md)
