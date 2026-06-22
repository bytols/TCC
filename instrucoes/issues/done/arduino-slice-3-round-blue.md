# Slice 3 — Início de rodada: BLUE em todos os totens + campo `round_started_at`

## Parent

[PRD: Integração Arduino — Totens LED por Jogador](arduino-led-totems.md)

## What to build

Quando o estado avança para qualquer `ROUND_X` (rodadas 1, 2 ou 3), todos os totens de players ativos devem acender em azul simultaneamente, comunicando no espaço físico que uma nova rodada de votação começou.

O campo `round_started_at` (DateTime nullable) é adicionado ao modelo `Session` e gravado a cada transição para `ROUND_X`. O timer da background task (Slice 4) usará esse ponto de partida para calcular quando enviar PINK e ORANGE.

## Acceptance criteria

- [ ] Modelo `Session` possui coluna `round_started_at` (DateTime, nullable).
- [ ] `advance_state()` atribui `round_started_at = datetime.utcnow()` em toda transição para `ROUND_1`, `ROUND_2` ou `ROUND_3`.
- [ ] Na mesma transição, `arduino.send_led(p.id, "BLUE")` é chamado para cada player ativo no banco.
- [ ] Players com slot vazio (sem player associado) não recebem nenhum comando.
- [ ] Teste de integração: após `LOBBY → ROUND_1`, `send_led` foi chamado com `"BLUE"` exatamente uma vez por player ativo, usando `patch("arduino.send_led")`.

## Blocked by

- [Slice 1 — Módulo `arduino.py`](arduino-slice-1-foundation.md)
