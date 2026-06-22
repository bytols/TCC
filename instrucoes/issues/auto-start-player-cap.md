# PRD: Auto-Start com Countdown e Limite de 4 Jogadores

## Problem Statement

O fluxo atual exige que o host (TV) clique manualmente em "INICIAR" para começar a sessão, o que cria fricção desnecessária em um contexto de apresentação/demo onde o host pode estar distante da tela. Além disso, o limite de 10 jogadores é maior do que o cenário de uso real (até 4 participantes), gerando expectativa errada sobre a escala da experiência.

## Solution

O jogo inicia automaticamente 30 segundos após o 2º jogador entrar no lobby, exibindo um countdown visível tanto na TV quanto nos celulares dos jogadores em espera. O host mantém o botão INICIAR como atalho para pular o countdown quando o grupo já estiver completo. O limite máximo de jogadores é reduzido de 10 para 4. O tempo do countdown é configurável via variável de ambiente.

## User Stories

1. Como host, quero que o jogo inicie automaticamente após um período de espera, para não precisar me aproximar da TV para clicar em INICIAR.
2. Como host, quero que o countdown comece apenas quando houver pelo menos 2 jogadores no lobby, para que o jogo nunca inicie sozinho.
3. Como host, quero que o countdown continue sem resetar quando novos jogadores entram durante a contagem, para não ficar preso em um loop infinito de espera.
4. Como host, quero poder clicar em INICIAR a qualquer momento durante o countdown para adiantar o início, para agilizar a experiência quando o grupo já estiver pronto.
5. Como host, quero que o countdown seja cancelado se o número de jogadores cair abaixo de 2 durante a contagem, para que o jogo não inicie sem jogadores suficientes.
6. Como jogador, quero ver um countdown na tela de espera do celular informando em quantos segundos o jogo vai começar, para saber que a experiência está prestes a iniciar.
7. Como jogador (na TV), quero ver o countdown na tela do lobby, para entender visualmente o estado da sessão.
8. Como jogador, quero que o limite de participantes seja 4 pessoas, para que a experiência seja calibrada para o grupo real.
9. Como jogador, quero ser informado que a sessão está cheia ao tentar entrar quando já há 4 participantes, para entender por que não consigo entrar.
10. Como host, quero configurar o tempo de countdown via variável de ambiente, para ajustar a experiência sem mexer no código.
11. Como jogador que ainda está preenchendo o formulário de join quando o countdown termina, quero ver a tela de sessão ativa ao submeter, para entender que perdi a janela de entrada.
12. Como host, quero que o botão INICIAR só funcione quando houver pelo menos 2 jogadores (comportamento atual mantido), para que o atalho manual também respeite o mínimo.

## Implementation Decisions

- `MAX_PLAYERS` em `config.py` muda de 10 para 4. A validação já existe nas rotas de join (GET e POST) — nenhuma nova lógica de guarda é necessária.

- `AUTO_START_SECONDS` é introduzido como variável de ambiente lida em `config.py` (padrão: 30). Deve estar documentada no `.env.example` do projeto.

- O countdown é implementado **inteiramente no cliente (JavaScript)**, sem timer server-side. A lógica é:
  - Quando o evento WebSocket `player_joined` (ou `state_change`) indica `player_count >= 2`, o cliente inicia um countdown local de `AUTO_START_SECONDS` segundos.
  - Quando o countdown atinge zero, o **desktop** chama `POST /admin/start`. O mobile apenas exibe — não dispara a chamada.
  - Se `player_count` cair abaixo de 2 (via evento), o countdown é cancelado e o UI volta ao estado de espera normal. Na prática, a ausência de detecção de desconexão de lobby torna este caso raro.
  - Se o host clicar em INICIAR durante o countdown, a chamada existente a `/admin/start` é executada imediatamente; o endpoint já é idempotente (valida estado LOBBY + ≥2 jogadores).

- O valor de `AUTO_START_SECONDS` precisa chegar ao frontend para que o countdown seja preciso. A abordagem recomendada: embutir o valor no contexto de template Jinja (variável JS global) em `desktop/lobby.html` e `mobile/waiting.html`, lido a partir de `config.AUTO_START_SECONDS`.

- O UI do countdown no **desktop** substitui ou complementa o texto atual de "Aguardando jogadores" quando `player_count >= 2`, exibindo "Começando em Xs".

- O UI do countdown no **mobile** (tela `/waiting`) exibe a contagem regressiva abaixo do ícone de TV existente, substituindo ou complementando "AGUARDE OS JOGADORES".

- O botão INICIAR no desktop permanece inalterado em comportamento — apenas chama `POST /admin/start`. O countdown no cliente é cancelado assim que o estado muda para `ROUND_1` via `state_change` WebSocket.

- `ROUND1_PICKS`, `ROUND2_PICKS` e `ROUND3_PICKS` permanecem em 5/3/3. O pool maior resultante com 4 jogadores é intencional e beneficia as chances de match.

## Testing Decisions

Bons testes verificam **comportamento observável pelo usuário**, não detalhes de implementação do countdown JS.

**O que testar:**

- `POST /admin/start` com exatamente 2 jogadores em LOBBY → retorna estado `ROUND_1`.
- `POST /admin/start` com 5 jogadores (acima do novo MAX_PLAYERS=4) → nunca deve ocorrer, pois o join já bloqueia; mas o endpoint deve continuar aceitando qualquer quantidade ≥ 2.
- `GET /join` com 4 jogadores já no lobby → renderiza `session_full.html` (comportamento existente, apenas o threshold muda).
- `POST /join` com 4 jogadores já no lobby → retorna 403 com `session_full.html`.
- Countdown no frontend: o teste mais útil é de integração (ex.: Playwright/Selenium) que verifica que, após o 2º jogador entrar, o texto de countdown aparece na tela de waiting e no desktop, e que após `AUTO_START_SECONDS` o estado muda para `ROUND_1`.

**Prior art:** as rotas de join já têm lógica de guarda testável via requisições HTTP diretas. O padrão de teste mais próximo no projeto é chamar os endpoints de rota diretamente com `flask test client` ou via requests.

## Out of Scope

- Detecção real de presença/desconexão de jogadores no lobby (sem WebSocket de heartbeat).
- Cancelamento do countdown quando um jogador fecha o browser (impossível sem presença).
- Aviso em tempo real no formulário de join de que o jogo está prestes a iniciar.
- Alteração nas quantidades de picks por rodada.
- Mudança no fluxo de rounds, algoritmo de match ou qualquer outra parte da máquina de estados.

## Further Notes

- O edge case "jogador preenche o formulário de join enquanto o countdown termina e o jogo inicia" resulta em `session_active.html` ao submeter — comportamento intencional e aceitável dado o contexto de uso.
- A variável `AUTO_START_SECONDS` no `.env` é o único ponto de configuração exposto. O valor padrão de 30 segundos foi escolhido para dar tempo a grupos de 3-4 pessoas de entrar antes do início, sem tornar a espera entediante.
- O countdown client-side é reiniciado se a página for recarregada. Não há persistência do tempo restante no servidor — é comportamento aceito.
