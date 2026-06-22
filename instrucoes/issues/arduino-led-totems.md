# PRD: Integração Arduino — Totens LED por Jogador

## Problem Statement

A experiência RUÍDO é visual e coletiva, mas os participantes ficam olhando apenas para seus celulares e para a TV. Não há nenhum elemento físico no espaço que represente cada jogador individualmente ou comunique o progresso da rodada de forma ambient. Durante uma sessão presencial, é difícil saber quem já terminou de votar sem consultar a tela da TV.

## Solution

Cada jogador passa a ter um totem físico — uma fita de LED RGB — que muda de cor em resposta ao estado do jogo. O servidor Flask envia comandos via serial USB para dois Arduinos que controlam as fitas. As cores seguem a mesma linguagem visual do design system (azul → rosa → laranja → branco/verde), tornando o progresso individual legível no espaço físico sem nenhuma interação extra do usuário.

## User Stories

1. Como espectador, quero ver qual totem está aceso em azul para saber quais jogadores estão ativamente escolhendo filmes nesta rodada.
2. Como espectador, quero ver um totem mudar para rosa para entender que aquele jogador está demorando mais que 2 minutos nesta rodada.
3. Como espectador, quero ver um totem mudar para laranja para entender que aquele jogador está com o tempo quase esgotado (mais de 4 minutos).
4. Como espectador, quero ver um totem acender em branco quando aquele jogador finalizar a votação, para saber que ele já terminou sem olhar para a TV.
5. Como espectador, quero ver todos os totens acenderem em verde quando o grupo atingir consenso, para que o momento de match tenha uma resposta física imediata.
6. Como espectador, quero que totens de slots vazios fiquem completamente apagados durante toda a sessão, para que apenas os participantes ativos estejam representados.
7. Como host, quero que os totens fiquem brancos quando os jogadores entram no lobby, para indicar presença antes da rodada começar.
8. Como host, quero que todos os totens voltem ao estado inicial (apagados ou padrão) quando encerrar a sessão, para que a instalação fique limpa entre sessões.
9. Como host, quero que o jogo continue normalmente caso a comunicação serial falhe, para que um problema de hardware não interrompa a experiência de votação.
10. Como host, quero configurar as portas seriais dos Arduinos via variável de ambiente, para não precisar alterar o código-fonte antes de cada apresentação.
11. Como host, quero que as cores dos totens nas rodadas 2 e 3 também sigam o timer reiniciado a cada rodada (azul → rosa → laranja), para que a urgência seja comunicada corretamente em cada fase.
12. Como jogador, quero que meu totem mostre branco assim que eu enviar meu voto, para ter confirmação física de que minha escolha foi registrada.
13. Como espectador, quero que os totens dos slots 1–2 sejam controlados pelo Arduino A e os dos slots 3–4 pelo Arduino B, para que a instalação física seja modular e tolerante a falha de um dos Arduinos.

## Implementation Decisions

- **Mapeamento de slots:** player_id 1 e 2 são gerenciados pelo Arduino A (slots locais S1 e S2); player_id 3 e 4 pelo Arduino B (slots locais S1 e S2). O servidor faz o roteamento — os dois Arduinos têm firmware idêntico e só conhecem S1/S2.

- **Protocolo serial:** mensagens de texto ASCII terminadas em `\n`, no formato `S{slot}:{COR}`. Cores válidas: `WHITE`, `BLUE`, `PINK`, `ORANGE`, `GREEN`. Exemplo: `S1:BLUE\n`. O Arduino faz `Serial.readStringUntil('\n')` e aplica a cor na fita correspondente.

- **Configuração de portas:** dois campos em `config.py`, populados via variável de ambiente:
  ```
  ARDUINO_A_PORT  (ex: /dev/tty.usbmodem1401)
  ARDUINO_B_PORT  (ex: /dev/tty.usbmodem1403)
  ARDUINO_BAUD    (padrão: 9600)
  ```
  Antes da apresentação, listar portas com `python -m serial.tools.list_ports` e atualizar o `.env`. Os dois Arduinos devem ter adesivo identificando A e B.

- **Novo módulo `arduino.py`:** responsável por abrir as portas seriais na inicialização da aplicação, rotear `send_led(player_id, color)` para o Arduino e slot corretos, e lidar silenciosamente com falhas de serial (try/except sem propagação). Exporta também `init()`, chamado em `app.py` após a factory do Flask.

- **Sequência de cores por evento:**

  | Evento no servidor | Ação nos LEDs |
  |---|---|
  | `player_joined` (LOBBY) | `send_led(player_id, "WHITE")` |
  | `advance_state()` → `ROUND_X` | todos os players ativos: `"BLUE"` + dispara timer |
  | Timer: +120s sem submeter | players não submetidos: `"PINK"` |
  | Timer: +120s adicionais sem submeter | players não submetidos: `"ORANGE"` |
  | `round_X/submit` (voto registrado) | `send_led(player_id, "WHITE")` |
  | `advance_state()` → `FINAL` | todos os players ativos: `"GREEN"` |
  | `clear_session()` | todos os slots ativos: `"WHITE"` (reset visual) |

- **Timer por rodada — background task com eventlet:** ao transicionar para qualquer estado `ROUND_X`, `advance_state()` dispara uma `socketio.start_background_task`. A task dorme 120s, consulta `submitted_player_ids(round)` para filtrar quem ainda não submeteu, envia `PINK` apenas para esses; dorme mais 120s, repete com `ORANGE`. Nenhuma flag de cancelamento é necessária — a checagem acontece no momento de agir, portanto se a rodada já tiver terminado a lista estará vazia e nenhum comando é enviado.

- **Campo `round_started_at` no modelo `Session`:** coluna `DateTime nullable=True` adicionada ao `Session`. É atribuída em `advance_state()` a cada transição para `ROUND_X`, de forma análoga ao `started_at` existente para o jogo inteiro. Usada para diagnóstico e possível exibição futura; o timer da background task é auto-suficiente (conta a partir do próprio `datetime.utcnow()` no momento do disparo).

- **Tratamento de falha silenciosa:** todo `port.write()` em `arduino.py` é envolvido em `try/except Exception: pass`. Se a porta não abrir na inicialização, o atributo interno fica `None` e `send_led` retorna sem fazer nada. O jogo nunca trava por causa do hardware.

- **`pyserial` adicionado a `requirements.txt`.**

## Testing Decisions

Bons testes verificam comportamento externo observável: qual player_id recebeu qual cor em qual momento. Não testam detalhes internos de `pyserial` ou da estrutura de threads eventlet.

**Seam principal — `arduino.send_led(player_id, color)`:** esta função é a fronteira entre a lógica do jogo e o hardware. Os testes mockam o objeto `serial.Serial` e assertam quais bytes foram escritos em qual porta. Esta é a camada mais alta possível que ainda isola o hardware.

**O que testar:**

- `send_led(1, "BLUE")` escreve `b"S1:BLUE\n"` na porta A e nada na porta B.
- `send_led(3, "ORANGE")` escreve `b"S1:ORANGE\n"` na porta B (remapeamento local de slot).
- `send_led(player_id, color)` com porta `None` (serial indisponível) não levanta exceção.
- `POST /join` (criação de player bem-sucedida) → `send_led` chamado com `"WHITE"` para o player_id criado.
- `POST /round/1/submit` (último jogador) → `send_led` chamado com `"WHITE"` para o player que submeteu, e a subsequente `advance_state()` pode emitir `"BLUE"` (próxima rodada) ou `"GREEN"` (FINAL).
- `advance_state()` transitando de `LOBBY` → `ROUND_1` → todos os players ativos recebem `"BLUE"`.
- `advance_state()` resultando em `FINAL` → todos os players ativos recebem `"GREEN"`.

**Prior art:** os testes existentes (`test_join_limit.py`, `test_slice2_countdown.py`) usam `app.test_client()` com fixtures de banco in-memory e mockam dependências externas via `unittest.mock.patch`. O mesmo padrão se aplica aqui: `patch("arduino.send_led")` nas rotas e `patch("arduino._port_a")` nos testes de unidade de `arduino.py`.

## Out of Scope

- Firmware do Arduino (sketch `.ino`) — responsabilidade separada do hardware.
- Controle de LEDs RGB individuais dentro de uma fita (efeitos, animações, gradientes) — a fita inteira recebe uma cor sólida.
- Reconexão automática da serial após falha em tempo de execução — a porta é aberta uma vez na inicialização.
- Detecção de qual Arduino está conectado em qual porta sem intervenção manual — a configuração é sempre explícita.
- Mais de 4 jogadores ou mais de 2 Arduinos.
- Integração com o timer de cores do desktop (`elapsed_seconds`) — os totens usam timer próprio reiniciado por rodada, independente da paleta de cores da TV.
- Interface de administração para testar os LEDs sem uma partida em andamento.

## Further Notes

- O macOS expõe Arduinos como `/dev/tty.usbmodem*` com sufixo derivado do número de série do chip CH340/FTDI. A ordem pode mudar se um Arduino for desconectado e reconectado. Por segurança, identificar as portas com `python -m serial.tools.list_ports -v` antes de cada apresentação e colar a configuração no `.env`.
- O Arduino reseta ao abrir a porta serial (toggle de DTR). Dependendo do firmware, pode ser necessário um `time.sleep(2)` após `serial.Serial(...)` em `arduino.init()` para aguardar o bootloader do Arduino.
- Com apenas 2 jogadores, o Arduino B não recebe nenhum comando durante toda a sessão — comportamento correto, totens 3 e 4 ficam apagados.
- A cor PINK no código corresponde à cor "rosa" do design system (`glow-pink`). O firmware do Arduino deve ser calibrado para aproximar o RGB da fita ao `#B6006F` da paleta quando receber `PINK`.
