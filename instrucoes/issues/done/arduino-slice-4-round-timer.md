# Slice 4 — Timer de rodada: PINK aos +2min, ORANGE aos +4min

## Parent

[PRD: Integração Arduino — Totens LED por Jogador](arduino-led-totems.md)

## What to build

Ao iniciar cada rodada, uma background task eventlet é disparada junto com o sinal BLUE. Ela aguarda 120 segundos e envia PINK apenas para os players que ainda não submeteram seus votos naquela rodada. Aguarda mais 120 segundos e envia ORANGE da mesma forma.

Nenhuma flag de cancelamento é necessária: a task consulta `submitted_player_ids(round)` no momento de agir. Se todos já submeteram (rodada encerrada antes do timer), a lista estará vazia e nenhum comando é enviado.

O timer reinicia a cada rodada — no início de ROUND_2 e ROUND_3, todos os totens voltam para BLUE e o contador recomeça do zero.

## Acceptance criteria

- [ ] Ao transicionar para `ROUND_X`, uma background task é lançada via `socketio.start_background_task`.
- [ ] Após 120s, a task envia `"PINK"` apenas para players que ainda não submeteram naquela rodada.
- [ ] Após mais 120s, a task envia `"ORANGE"` apenas para players que ainda não submeteram.
- [ ] Se todos os players já submeteram quando o timer dispara, nenhum comando é enviado.
- [ ] O timer reinicia corretamente nas rodadas 2 e 3 (ROUND_2 e ROUND_3 também disparam a task).
- [ ] Teste: com `patch("arduino.send_led")` e `patch("eventlet.sleep")` (ou similar), verificar que PINK é enviado apenas para players não-submetidos no momento do disparo.

## Blocked by

- [Slice 3 — Início de rodada: BLUE + `round_started_at`](arduino-slice-3-round-blue.md)
