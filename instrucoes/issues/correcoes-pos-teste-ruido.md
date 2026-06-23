# PRD: Correções pós-teste — RUÍDO (LEDs, tela final, posters, performance, avatar)

> Status: ready-for-agent

## Problem Statement

Em uma sessão de teste presencial da experiência RUÍDO, o grupo identificou um conjunto de defeitos que quebram a experiência tanto na instalação física (totens LED) quanto nas telas mobile e de TV:

- Os totens LED **iniciam com cores diferentes** entre si quando a aplicação sobe, em vez de um estado limpo e uniforme.
- As cores dos **LEDs e do fundo da TV mudam em momentos diferentes** — não há sensação de que o espaço físico e a tela contam a mesma história de tempo.
- Ao terminar a votação, o LED de um jogador **não fica branco de forma confiável**: o segundo jogador, ao concluir suas escolhas e ir para a tela de resultado parcial, ficou **laranja** em vez de branco.
- No mobile, os **posters dos filmes não aparecem no carrossel** — só surgem quando o jogador toca no filme e abre o modal.
- Nas **telas intermediárias de consenso** (resultado das rodadas 1 e 2 na TV), os posters não aparecem.
- A **tela final de consenso no desktop está completamente quebrada** — sem layout, totalmente diferente do design do Figma.
- A aplicação **trava e fica pouco responsiva no mobile em todas as telas** — desde o primeiro botão "INICIAR" até o fim, com toques lentos e travamentos.
- A **personalização de personagem** é visualmente pobre, pouco alinhada à identidade RUÍDO, e apresenta bugs (estado não preservado ao trocar de aba, opções nem sempre refletidas no preview).

## Solution

Do ponto de vista de quem usa a experiência:

- Ao ligar a aplicação, **todos os totens ficam apagados** (estado limpo e uniforme) e cada totem **acende em branco quando o jogador correspondente entra** no lobby.
- LEDs e fundo da TV passam a seguir **um único relógio, no servidor**, com cadência de **2 minutos** e **reset a cada rodada**: toda rodada recomeça em azul (totens + TV) e evolui azul → rosa → laranja em sincronia. Quando um jogador termina, **apenas o totem dele** fica branco; os demais continuam evoluindo de cor junto com a TV.
- Ao terminar a votação, o totem do jogador fica **branco e assim permanece** — nenhuma fase de timer de uma rodada já encerrada o sobrescreve.
- No mobile, os **posters aparecem direto no carrossel**, sem precisar tocar.
- As **telas intermediárias de consenso na TV exibem o poster real** do filme.
- A **tela final no desktop reflete o design do Figma**: zona esquerda com "RESULTADO COLETIVO" + subtítulo + card de TEMPO + avatares dos jogadores; zona central com os posters do(s) filme(s) de consenso; zona direita com "FILME ESCOLHIDO" + título + metadados; tagline e wordmark no rodapé.
- A experiência mobile fica **fluida e responsiva** em todas as telas.
- A personalização de personagem fica **mais rica e estilizada conforme a identidade RUÍDO**, com bugs corrigidos.

## User Stories

### Totens LED

1. Como host, quero que ao subir a aplicação todos os totens fiquem apagados, para que a instalação comece num estado limpo e uniforme.
2. Como host, quero que o totem de um jogador acenda em branco assim que ele entra no lobby, para indicar presença antes da rodada começar.
3. Como espectador, quero que no início de cada rodada todos os totens ativos acendam em azul, para entender que uma nova fase de escolha começou.
4. Como espectador, quero que os totens dos jogadores que ainda estão escolhendo evoluam de azul para rosa para laranja a cada 2 minutos, para sentir a urgência crescente da rodada.
5. Como espectador, quero que a cada nova rodada a contagem de cor reinicie em azul, para que a urgência seja comunicada por rodada e não pelo jogo inteiro.
6. Como jogador, quero que meu totem fique branco assim que eu enviar meu voto, para ter confirmação física de que terminei.
7. Como jogador, quero que meu totem permaneça branco depois que eu terminar, mesmo enquanto os outros continuam jogando, para que minha conclusão não seja revertida para outra cor.
8. Como espectador, quero ver os totens dos demais jogadores continuarem mudando de cor enquanto um já terminou, para distinguir quem concluiu de quem ainda está escolhendo.
9. Como espectador, quero ver todos os totens ativos ficarem verdes quando o grupo atinge consenso, para que o match tenha resposta física imediata.
10. Como host, quero que os totens de slots sem jogador permaneçam apagados durante toda a sessão, para que apenas participantes ativos estejam representados.
11. Como host, quero que o jogo continue normalmente se a comunicação serial falhar, para que um problema de hardware não interrompa a votação.

### Sincronização TV ↔ LED

12. Como espectador, quero que o fundo da TV e os totens mostrem a mesma cor de fase e mudem nos mesmos instantes, para que a tela e o espaço físico contem a mesma história.
13. Como espectador, quero que o fundo da TV reinicie em azul a cada rodada, junto com os totens, para manter a coerência entre tela e instalação.
14. Como espectador, quero que no consenso o fundo da TV fique verde junto com os totens, para reforçar o momento de match.

### Posters no mobile (carrossel)

15. Como jogador, quero ver o poster do filme direto no card central do carrossel, sem precisar tocar, para reconhecer o filme rapidamente.
16. Como jogador, quero ver os posters também nos cards vizinhos do deck, para navegar visualmente.
17. Como jogador num celular mais antigo, quero que os posters apareçam corretamente mesmo que o layout dependa de proporção de imagem, para não ver cards vazios.

### Posters nas telas intermediárias da TV

18. Como espectador, quero ver o poster real de cada filme no resultado da rodada 1 e da rodada 2 na TV, para reconhecer os filmes em disputa.
19. Como espectador, quero que, quando não houver poster disponível, apareça um placeholder consistente (gradiente + inicial), para que a tela não fique quebrada.

### Tela final desktop

20. Como espectador, quero ver "RESULTADO COLETIVO" com subtítulo na zona esquerda da tela final, para entender o que estou vendo.
21. Como espectador, quero ver o card de TEMPO com a duração da sessão na zona esquerda, para saber quanto tempo o grupo levou.
22. Como espectador, quero ver os avatares dos jogadores na tela final, para reconhecer quem participou.
23. Como espectador, quero ver os posters do(s) filme(s) de consenso em destaque no centro, todos do mesmo tamanho quando houver mais de um, para ver o resultado coletivo.
24. Como espectador, quero ver "FILME ESCOLHIDO" com título e metadados (ano · gênero) na zona direita, para identificar o filme vencedor.
25. Como espectador, quero ver a tagline e o wordmark RUÍDO no rodapé, para fechar a experiência com a marca.
26. Como host, quero acessar a ação de encerrar a sessão a partir da tela final, para limpar a instalação entre sessões.
27. Como espectador, quero que a tela final tenha layout organizado e fiel ao Figma em telas grandes, sem elementos sobrepostos ou fora do fluxo.

### Performance mobile

28. Como jogador, quero que a tela inicial e o botão INICIAR respondam imediatamente ao toque, para começar sem frustração.
29. Como jogador, quero rolar e tocar em qualquer tela do mobile sem travamentos, para uma experiência fluida.
30. Como jogador, quero que o carrossel de filmes deslize suavemente, para escolher filmes confortavelmente.
31. Como jogador num iPhone/Safari, quero a mesma fluidez de outros aparelhos, para não ser penalizado pelo meu dispositivo.

### Personalização de personagem

32. Como jogador, quero que minhas escolhas de avatar sejam preservadas ao alternar entre as abas de personalização, para não perder o que já configurei.
33. Como jogador, quero que cada opção selecionada seja imediatamente refletida no preview do avatar, para ver o resultado enquanto monto.
34. Como jogador, quero uma tela de personalização visualmente rica e alinhada à identidade RUÍDO, para que a criação de identidade seja parte da experiência.
35. Como jogador, quero feedback visual claro ao selecionar uma opção (destaque/glow/borda), para saber o que está ativo.
36. Como jogador, quero que minha escolha de avatar persista durante toda a sessão, para que minha identidade seja consistente nas telas seguintes.

## Implementation Decisions

### Totens LED e sincronização (módulos: `arduino`, `session_state`, `routes/game`, `static/js/desktop.js`)

- **Estado inicial apagado:** `arduino.init()` passa a chamar uma rotina de reset que envia o comando de "apagar" para os quatro slots (S1/S2 dos dois Arduinos). É preciso uma cor/estado **`OFF`** no protocolo serial (`S{slot}:OFF`), interpretada pelo firmware como totem apagado. `player_joined` continua enviando `WHITE`.

- **Fonte única de tempo no servidor:** a task de timer de rodada (`session_state`) passa a ser a **única fonte da verdade** para a fase de cor. Em cada fronteira de fase ela (a) emite um evento WebSocket de fase para a TV e (b) aciona os LEDs dos jogadores que ainda não submeteram. Cadência: azul no início da rodada (já emitido na transição), rosa após 2 min, laranja após mais 2 min. **Reset por rodada** (cada `ROUND_x` reinicia em azul, LEDs + TV).

- **Novo evento WebSocket `round_phase`:** payload mínimo `{ "color": "BLUE" | "PINK" | "ORANGE" }`, emitido no room `game_room`. O `desktop.js` deixa de calcular cor por `elapsed_seconds` (timer do cliente) e passa a aplicar a classe `glow-*` no `#desktop-app` ao receber `round_phase`; `state_change` para `FINAL` aplica verde; início de `ROUND_x` aplica azul. Isso elimina os dois relógios divergentes.

- **LED por jogador preservado:** as fases rosa/laranja continuam sendo enviadas **apenas para jogadores que ainda não submeteram** (`submitted_player_ids`). Quem submeteu recebeu branco e não é tocado pela task.

- **Guard de geração para o timer de rodada (corrige LED laranja indevido):** o modelo `Session` ganha um contador de geração de timer (ex.: inteiro incrementado em `advance_state()` a cada transição para `ROUND_x`). A task recebe a geração no disparo e, antes de aplicar qualquer fase, valida que (a) a geração ainda é a corrente e (b) o estado ainda é a rodada esperada. Se a rodada terminou (último submit levou a SHOW/FINAL) ou outra rodada começou, a task aborta sem enviar cor. Assim o `WHITE` do submit é definitivo e não é sobrescrito por uma fase tardia da rodada encerrada.

  ```
  # esboço da decisão (não é o código final)
  advance_state(): ao entrar em ROUND_x -> session.timer_gen += 1; dispara task(round, gen)
  task(round, gen):
      sleep(120); if stale(round, gen): return; emit round_phase PINK + send PINK aos não-submetidos
      sleep(120); if stale(round, gen): return; emit round_phase ORANGE + send ORANGE aos não-submetidos
  stale(round, gen): session.timer_gen != gen  or  session.state != f"ROUND_{round}"
  ```

- **Encerramento da sessão:** `clear_session()` continua resetando os totens (apagar/branco) de forma coerente com o estado inicial.

### Posters no carrossel mobile (módulos: `static/css/main.css`, `static/js/round.js`)

- A causa é **colapso de layout**, não lazy-load/CORS: o card do deck depende de `aspect-ratio` dentro de um container flexível que pode colapsar a altura no mobile, deixando o `.deck-poster` com altura zero (background invisível). O modal funciona por ser full-screen.
- Decisão: dar **altura concreta** ao palco do deck e um **fallback de altura** ao card (independente de `aspect-ratio`), garantindo que `background-size: cover` tenha área para pintar. Validar em viewport mobile.

### Posters nas telas intermediárias da TV (módulo: `templates/desktop/lobby.html`, `static/css/main.css`)

- As telas SHOW_1/SHOW_2 hoje ignoram o campo `poster` (já injetado em `routes/game`) e renderizam um gradiente fixo + inicial. Decisão: renderizar `background-image` do poster quando presente, com o mesmo padrão `has-poster` / placeholder usado na tela final, incluindo a regra CSS `background-size: cover`.

### Tela final desktop (módulos: `templates/desktop/lobby.html`, `static/css/main.css`)

- A marcação da tela final existe, mas **as classes CSS correspondentes não existem** em `main.css` — por isso renderiza com defaults do browser. Decisão: **reestruturar a marcação para o layout de 3 zonas do Figma e escrever o CSS faltante.**
- Layout (Figma node `254-5321`): zona esquerda (RESULTADO COLETIVO + subtítulo + card TEMPO + linha de avatares), zona central (posters do consenso), zona direita (FILME ESCOLHIDO + título + metadados ano/gênero), rodapé (tagline + wordmark RUÍDO), barra de gradiente no topo.
- **Caso multi-filme (decisão do desenvolvedor):** quando o consenso tiver mais de um filme, exibir os posters **todos do mesmo tamanho em linha** (sem herói central). Com um único filme, exibe um poster.
- A ação **ENCERRAR SESSÃO** permanece acessível na tela final.
- Medidas/tokens de cor e espaçamento devem ser extraídos do Figma (`get_design_context` do node) e mapeados aos tokens existentes do design system.

### Performance mobile (módulos: `static/css/main.css`, `templates/base_mobile.html`, `static/js/round.js`)

- Causa principal do travamento global: a camada de glow (`.glow-layer::before/::after`) **anima um blur de raio grande (95–105px) em tela cheia, infinitamente**, e há ~15 elementos empilhando `backdrop-filter: blur()` sobre essa superfície borrada em movimento — combinação cara para a GPU mobile, presente em todas as telas.
- Decisões:
  - Não animar o blur: pré-borrar o blob e animar apenas `transform`, ou desligar a animação no mobile (media query coarse pointer) e reduzir o raio do blur.
  - Reduzir o raio do `--glass-blur` no mobile e remover `backdrop-filter` de elementos que rolam (cards de lista), usando fundo translúcido sólido como fallback.
  - No deck, montar/decodificar apenas os cards visíveis (não o catálogo inteiro), usando atributos de decodificação e `content-visibility` para os fora de tela.
  - Revisar listeners de gesto/`requestAnimationFrame` do deck para evitar acúmulo.

### Personalização de personagem (módulos: `templates/mobile/join.html`, `static/js/avatar.js`, `static/css/main.css`, possivelmente `data/character_options.py`)

- Corrigir bugs: preservar a seleção ao alternar abas; garantir que toda mudança de opção atualize o preview SVG; confirmar persistência via `character_json`.
- Enriquecer visualmente seguindo a identidade RUÍDO (glassmorphism, paleta azul → rosa → laranja, tema ruído → consenso): estilizar abas e swatches conforme o design system, feedback de seleção (glow/borda), preview maior e mais nítido.
- O escopo visual exato será proposto e iterado com o desenvolvedor; opções novas de avatar só se necessárias para a identidade.

## Testing Decisions

Bons testes verificam **comportamento externo observável** — qual cor foi enviada a qual jogador em qual momento, qual evento foi emitido, o que a tela renderiza — e não detalhes internos de `pyserial`, eventlet ou da estrutura de threads.

- **Seam de hardware — `arduino.send_led(player_id, color)`:** mockar os objetos de porta e assertar os bytes escritos (`b"S1:OFF\n"`, `b"S2:WHITE\n"` etc.). Prior art: `tests/test_arduino.py`.
  - `arduino.init()` chama o reset e envia `OFF` aos quatro slots na inicialização.
  - `send_led` com porta `None` não levanta exceção.
- **Seam de transição de estado — `session_state.advance_state()` e as rotas `/round/x/submit`:** com `patch("arduino.send_led")` e `patch` no emissor de socket, assertar:
  - entrada em `ROUND_x` envia `BLUE` a todos os ativos e emite `round_phase BLUE`;
  - `FINAL` envia `GREEN` a todos os ativos e sinaliza verde;
  - submit envia `WHITE` ao jogador que submeteu;
  - a fase rosa/laranja só vai para jogadores **não** submetidos;
  - **guard de geração:** uma fase de timer cuja geração/estado não bate **não** envia cor (cobre o bug do LED laranja do último jogador). Prior art: `tests/test_slice4_round_timer.py`, `test_slice5_submit_white.py`, `test_slice6_final_green.py`.
- **Seam de evento WebSocket — `round_phase`:** assertar que a task emite o evento com a cor correta no momento correto (mock do emissor), no mesmo ponto em que aciona os LEDs.
- **Seam de renderização — `GET /desktop`:** com manifesto de posters injetado por monkeypatch, assertar:
  - tela final renderiza as zonas esperadas (RESULTADO COLETIVO, TEMPO, avatares, posters de consenso, FILME ESCOLHIDO) e os posters reais;
  - SHOW_1/SHOW_2 renderizam o poster real quando presente e placeholder quando ausente. Prior art: `tests/test_slice_final_tv_layout.py`, `test_slice_final_time_avatars.py`, `test_slice3_local_poster.py`.
- **Performance e ajustes puramente de CSS/carrossel mobile** são validados manualmente em viewport mobile (inclusive Safari iOS) — não há asserção automatizada de FPS; o que for testável (presença de `has-poster`, altura concreta do deck) pode ser coberto por teste de template.

## Out of Scope

- Firmware do Arduino (`.ino`) e calibração fina de cor (ex.: o laranja parecer amarelado é responsabilidade do firmware/hardware). O servidor só envia nomes de cor padronizados.
- Reconexão automática da serial em tempo de execução — a porta é aberta uma vez na inicialização.
- Suporte a mais de 4 jogadores ou mais de 2 Arduinos.
- Fonte de dados real de posters/sinopses além do que já existe (manifesto local + TMDB opcional).
- Redesenho das telas mobile que já estão aprovadas (a tela final mobile, por exemplo, está OK).
- Métricas/instrumentação automatizada de performance (FPS, profiling em CI).

## Further Notes

- O tracker do projeto são arquivos markdown em `instrucoes/issues/` (movidos para `done/` ao concluir), no mesmo formato deste PRD (ver `arduino-led-totems.md`).
- A integração Arduino já existe no código (`arduino.py`, fiação em `session_state.py`) mas **não está documentada no `CLAUDE.md`** — vale atualizar a doc ao implementar.
- Decisões fechadas com o desenvolvedor nesta sessão: estado inicial dos LEDs = apagados (branco ao entrar); cadência única de 2 min com reset por rodada e TV espelhando a cor de fase; tela final em linha de posters iguais; performance tratada de forma sistêmica (blur animado + backdrop-filter); avatar com correção de bugs + enriquecimento na identidade RUÍDO.
- Sugestão de ordem de execução: (1) bloco LED, (2) tela final desktop + posters SHOW, (3) carrossel mobile + performance, (4) avatar.
- O design da tela final está no Figma: node `254-5321` do arquivo `1ea5BjwNJjsAWMgq430V00`.
