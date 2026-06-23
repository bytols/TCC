# Slice LED 3 — Guard de geração: LED concluído permanece branco

> Status: ready-for-agent

## Parent

`instrucoes/issues/correcoes-pos-teste-ruido.md`

## What to build

Quando o último jogador termina a votação e a tela avança para o resultado parcial, o totem dele pode ficar **laranja em vez de branco**: uma fase tardia do timer da rodada (já encerrada) sobrescreve o branco do submit.

Esta slice torna o branco do submit definitivo via **guard de geração** na task de timer de rodada. O modelo `Session` ganha um contador de geração incrementado a cada transição para `ROUND_x`; a task recebe a geração no disparo e, antes de aplicar qualquer fase, valida que a geração ainda é a corrente **e** que o estado ainda é a rodada esperada. Se a rodada terminou ou outra começou, a task aborta sem enviar cor.

Esboço da decisão (de protótipo — não é o código final):

```
advance_state(): ao entrar em ROUND_x -> session.timer_gen += 1; dispara task(round, gen)
task(round, gen):
    sleep(120); if stale(round, gen): return; aplica fase PINK
    sleep(120); if stale(round, gen): return; aplica fase ORANGE
stale(round, gen): session.timer_gen != gen  or  session.state != f"ROUND_{round}"
```

## Acceptance criteria

- [ ] `Session` tem um contador de geração de timer, incrementado a cada entrada em `ROUND_x`.
- [ ] Uma fase de timer cuja geração não é mais a corrente **não** envia cor nem emite evento.
- [ ] Uma fase de timer cujo estado já não é a rodada esperada (ex.: já em SHOW/FINAL) **não** envia cor.
- [ ] Cenário do bug coberto por teste: jogador que submeteu por último mantém branco; nenhuma fase posterior da rodada encerrada o sobrescreve. Segue `tests/test_slice4_round_timer.py` / `test_slice5_submit_white.py`.

## Blocked by

- `instrucoes/issues/slice-led-2-timer-unico-round-phase.md` (reestrutura a mesma task de timer)
