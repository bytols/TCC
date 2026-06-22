# Slice 2 — Presença no lobby: WHITE ao entrar

## Parent

[PRD: Integração Arduino — Totens LED por Jogador](arduino-led-totems.md)

## What to build

Quando um jogador entra no lobby e sua identidade é criada com sucesso (após `POST /join`), o totem correspondente deve acender em branco, sinalizando presença física antes de qualquer rodada começar.

Além disso, `arduino.init()` deve ser chamado durante a inicialização da aplicação Flask para que as portas seriais estejam abertas desde o startup do servidor.

## Acceptance criteria

- [ ] `app.py` chama `arduino.init()` após criar a aplicação Flask.
- [ ] `POST /join` com dados válidos → `arduino.send_led(player.id, "WHITE")` é chamado após o player ser persistido no banco.
- [ ] `POST /join` que falha por validação (nome inválido, lobby cheio, etc.) → `send_led` não é chamado.
- [ ] Teste de integração: `POST /join` bem-sucedido → `send_led` foi chamado com `(player_id, "WHITE")`, usando `patch("arduino.send_led")`.

## Blocked by

- [Slice 1 — Módulo `arduino.py`](arduino-slice-1-foundation.md)
