# Slice LED 1 — LEDs apagados no boot (estado inicial uniforme)

> Status: ready-for-agent

## Parent

`instrucoes/issues/correcoes-pos-teste-ruido.md`

## What to build

Ao subir a aplicação, todos os totens devem ficar **apagados** (estado limpo e uniforme), em vez de manter cores aleatórias deixadas pelo firmware. Cada totem continua acendendo em **branco** quando o jogador correspondente entra no lobby (comportamento já existente).

Para isso o protocolo serial ganha um estado **`OFF`** (`S{slot}:OFF`) e a inicialização da camada Arduino passa a enviar `OFF` para os quatro slots (S1/S2 dos dois Arduinos) logo após abrir as portas. Se a serial estiver indisponível, nada deve falhar — o jogo segue normal.

A interpretação de `OFF` no firmware (apagar a fita) é responsabilidade do sketch e está fora do escopo desta issue; aqui entregamos apenas o envio correto pelo servidor.

## Acceptance criteria

- [ ] A inicialização da camada Arduino envia `OFF` para os 4 slots (Arduino A slots 1–2, Arduino B slots 1–2) ao subir a aplicação.
- [ ] `send_led(player_id, "OFF")` escreve `b"S{slot}:OFF\n"` na porta correta, respeitando o remapeamento de slot (jogadores 3–4 → Arduino B).
- [ ] Com porta serial indisponível (`None`), a inicialização e o envio de `OFF` não levantam exceção.
- [ ] O comportamento de "branco ao entrar" (player_joined → WHITE) permanece intacto.
- [ ] Testes no seam `arduino.send_led` / `arduino.init()` (mock das portas) cobrem os bytes enviados, seguindo o padrão de `tests/test_arduino.py`.

## Blocked by

None - can start immediately
