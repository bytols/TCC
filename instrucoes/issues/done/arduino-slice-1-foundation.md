# Slice 1 — Módulo `arduino.py`: serial manager, config e pyserial

## Parent

[PRD: Integração Arduino — Totens LED por Jogador](arduino-led-totems.md)

## What to build

Criar o módulo `arduino.py` que encapsula toda a comunicação serial com os dois Arduinos. O módulo deve abrir as portas seriais na inicialização da aplicação, rotear o comando `send_led(player_id, color)` para o Arduino e slot local corretos, e absorver silenciosamente qualquer falha de hardware — o jogo nunca pode travar por causa da serial.

Roteamento de slots: player_id 1–2 → Arduino A, slots locais S1/S2; player_id 3–4 → Arduino B, slots locais S1/S2. Os dois Arduinos têm firmware idêntico e só conhecem S1/S2.

Protocolo: mensagem ASCII `S{slot}:{COR}\n`. Cores válidas: `WHITE`, `BLUE`, `PINK`, `ORANGE`, `GREEN`. Exemplo: `S2:ORANGE\n`.

As portas seriais e o baud rate são configurados via variáveis de ambiente lidas em `config.py`, documentadas em `.env.example`. Nenhum hook em rotas de jogo neste slice — o módulo existe e é testável de forma isolada.

## Acceptance criteria

- [ ] `arduino.py` expõe `init()` e `send_led(player_id, color)`.
- [ ] `send_led(1, "BLUE")` escreve `b"S1:BLUE\n"` na porta A e nada na porta B.
- [ ] `send_led(3, "ORANGE")` escreve `b"S1:ORANGE\n"` na porta B (slot local 1).
- [ ] `send_led(4, "WHITE")` escreve `b"S2:WHITE\n"` na porta B (slot local 2).
- [ ] Quando a porta serial não está disponível (`None`), `send_led` retorna sem levantar exceção.
- [ ] `config.py` lê `ARDUINO_A_PORT`, `ARDUINO_B_PORT` e `ARDUINO_BAUD` do ambiente (padrão: `""`, `""`, `9600`).
- [ ] `.env.example` documenta as três variáveis com exemplos de valor para macOS.
- [ ] `pyserial` adicionado a `requirements.txt`.
- [ ] Testes unitários cobrem roteamento correto e falha silenciosa (porta `None`), usando mock de `serial.Serial`.

## Blocked by

Nenhum — pode começar imediatamente.
