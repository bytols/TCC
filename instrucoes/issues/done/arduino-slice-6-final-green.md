# Slice 6 — Consenso e encerramento: GREEN no FINAL, WHITE no reset

## Parent

[PRD: Integração Arduino — Totens LED por Jogador](arduino-led-totems.md)

## What to build

Quando o jogo atinge o estado FINAL — seja por match antecipado em qualquer rodada ou ao término natural da ROUND_3 — todos os totens de players ativos acendem em verde simultaneamente, marcando o momento de consenso no espaço físico.

Quando o host encerra a sessão (`/admin/end` → `clear_session()`), todos os slots ativos recebem WHITE como reset visual, deixando a instalação limpa para a próxima sessão.

O FINAL pode ser atingido por dois caminhos em `advance_state()`: retorno antecipado quando `has_match()` é verdadeiro em qualquer rodada, e transição normal de ROUND_3. O GREEN deve ser enviado em ambos os casos.

## Acceptance criteria

- [ ] Match antecipado (has_match em ROUND_1, ROUND_2 ou ROUND_3) → `advance_state()` envia `"GREEN"` para todos os players ativos antes de retornar.
- [ ] Transição normal ROUND_3 → FINAL (sem match) → `advance_state()` envia `"GREEN"` para todos os players ativos.
- [ ] `clear_session()` envia `"WHITE"` para todos os players ativos antes de apagar o banco.
- [ ] Slots sem player ativo não recebem nenhum comando em nenhum dos cenários.
- [ ] Teste de integração: estado FINAL por match antecipado → `send_led` chamado com `"GREEN"` para cada player ativo, usando `patch("arduino.send_led")`.
- [ ] Teste de integração: `clear_session()` → `send_led` chamado com `"WHITE"` para cada player ativo.

## Blocked by

- [Slice 1 — Módulo `arduino.py`](arduino-slice-1-foundation.md)
