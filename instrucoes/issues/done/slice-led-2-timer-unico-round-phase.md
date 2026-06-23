# Slice LED 2 — Timer único no servidor + sincronização TV ↔ LED (round_phase)

> Status: ready-for-agent

## Parent

`instrucoes/issues/correcoes-pos-teste-ruido.md`

## What to build

Hoje o fundo da TV muda de cor por um relógio do cliente (tempo desde o início do jogo, 3/6 min) e os LEDs mudam por um relógio próprio da rodada (2/4 min) — os dois ficam fora de sincronia. Esta slice unifica tudo em **uma única fonte de tempo no servidor**.

A task de timer de rodada passa a, em cada fronteira de fase, **emitir um evento WebSocket de fase** para a TV e **acionar os LEDs** dos jogadores que ainda não submeteram, no mesmo instante. Cadência: **azul** no início da rodada, **rosa** após 2 min, **laranja** após mais 2 min. A contagem **reinicia a cada rodada** (todo `ROUND_x` recomeça em azul, na TV e nos totens). No consenso (`FINAL`), TV e totens ficam **verdes**.

O `desktop.js` deixa de calcular cor por tempo decorrido no cliente e passa a aplicar a classe `glow-*` no app a partir do novo evento; início de rodada aplica azul, `FINAL` aplica verde.

Novo evento WebSocket no room `game_room`:

```
round_phase  ->  { "color": "BLUE" | "PINK" | "ORANGE" }
```

As fases rosa/laranja continuam por jogador: só vão para quem **ainda não submeteu**; quem submeteu já recebeu branco e não é tocado.

## Acceptance criteria

- [ ] Ao entrar em qualquer `ROUND_x`, servidor envia `BLUE` a todos os jogadores ativos e a TV mostra azul (reset por rodada).
- [ ] Após 2 min sem submeter, jogadores pendentes recebem `PINK` e o servidor emite `round_phase {color:"PINK"}`; após mais 2 min, idem com `ORANGE`.
- [ ] O evento `round_phase` e o acionamento dos LEDs acontecem no mesmo ponto (mesma fronteira de fase).
- [ ] `desktop.js` aplica a cor de fundo a partir de `round_phase` / estado, sem depender de `elapsed_seconds`.
- [ ] No `FINAL`, TV e totens ficam verdes.
- [ ] Fases rosa/laranja só atingem jogadores que ainda não submeteram.
- [ ] Testes (mock de `arduino.send_led` e do emissor de socket) cobrem: BLUE no início da rodada, emissão de `round_phase` por fase, GREEN no FINAL, e filtragem por não-submetidos — seguindo `tests/test_slice4_round_timer.py` e `test_slice6_final_green.py`.

## Blocked by

None - can start immediately
