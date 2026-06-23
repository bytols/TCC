# PRD — Revisão visual da tela de resultado final / consenso (RUÍDO)

> Status: ready-for-agent
> Sem issue tracker configurado neste repo; este PRD vive como arquivo até existir um tracker.
> Referência de design: Figma V3 — frame "FIM" (TV), node `254:5321`
> (`https://www.figma.com/design/1ea5BjwNJjsAWMgq430V00/...?node-id=5-6900`).

## Problem Statement

A tela final (estado `FINAL`) na TV/desktop está com aspecto estranho e inconsistente com o design V3. Hoje o host vê a **mesma grade de filmes** que aparece nas telas de resultado intermediário (`SHOW_1`/`SHOW_2`): uma lista de todos os filmes votados, cada um representado por um quadrado cinza com a inicial do título — sem poster, sem destaque para o consenso, sem o momento de "revelação coletiva" que o design pede.

O Figma define o `FINAL` como uma tela **completamente diferente** das telas de rodada intermediária: o(s) filme(s) de consenso aparecem em destaque com **poster real**, ao lado de "RESULTADO COLETIVO", do **tempo total** da experiência num cartão próprio e dos **avatares** dos participantes. É o clímax da jornada (ruído → consenso, fundo verde), e a tela atual não entrega esse momento.

Para uma defesa de TCC, a tela final é a que mais comunica o conceito do projeto; ela precisa estar visualmente alinhada ao design e mostrar a escolha do grupo de forma celebrativa, não como mais uma lista.

## Solution

Separar o estado `FINAL` num layout próprio na TV, fiel ao Figma V3, mantendo a grade atual apenas para `SHOW_1`/`SHOW_2` (que são telas de "ainda não houve consenso, próxima rodada" e funcionam bem como lista).

Da perspectiva do host na TV, no `FINAL`:

- Uma coluna de informação à esquerda: título "RESULTADO COLETIVO", a frase "Depois de diferentes escolhas, o grupo chegou a um consenso.", um **cartão de tempo** (rótulo "TEMPO" sobre o tempo total em `MM:SS`) e a **linha de avatares** dos participantes.
- O(s) **filme(s) de consenso** em destaque ao centro, com **poster real**. Quando há **um único** filme de consenso, ele aparece grande e centralizado (o "herói" do Figma); quando há **mais de um**, eles viram uma **fileira de posters** menores, cada um com seu título embaixo. A coluna singular "FILME ESCOLHIDO" do mockup sai, porque deixa de fazer sentido com vários filmes.
- Fundo no estado de consenso (verde) e o wordmark RUÍDO, como nas demais telas de TV.

O poster real depende de um pré-requisito já previsto no projeto: o **manifesto de posters** (`data/posters.json`) precisa estar populado pelo resolvedor (`resolve_posters.py`). Sem poster resolvido para um filme, o cartão cai no placeholder de gradiente existente (rede de segurança), sem quebrar a tela.

A tela de resultado **mobile** (`results.html`) passa a herdar o poster real nos itens (enriquecimento compartilhado), mas seu redesenho visual V3 fica como trabalho separado.

## User Stories

1. Como host na TV, quero que a tela final seja visualmente distinta das telas de resultado intermediário, para que o momento de consenso seja percebido como o clímax da experiência.
2. Como host na TV, quero ver o(s) filme(s) escolhido(s) pelo grupo com poster real em destaque, para revelar a decisão coletiva de forma celebrativa.
3. Como host na TV, quero ver mais de um filme quando o grupo chega a consenso em múltiplos títulos, para que nenhuma escolha coletiva seja escondida.
4. Como host na TV, quando há um único filme de consenso, quero que ele apareça grande e centralizado, para que a escolha do grupo seja inequívoca.
5. Como host na TV, quando há vários filmes de consenso, quero vê-los numa fileira de posters com seus títulos, para comparar as escolhas coletivas lado a lado.
6. Como host na TV, quero ver o tempo total da experiência num cartão destacado, para reforçar quanto tempo o grupo levou até convergir.
7. Como host na TV, quero ver os avatares dos participantes na tela final, para reconhecer quem participou da decisão.
8. Como host na TV, quero ler "RESULTADO COLETIVO" e a frase de fechamento, para entender que a jornada terminou em consenso.
9. Como host na TV, quero que a tela final use o estado de cor de consenso (verde), para fechar visualmente a transição ruído → consenso.
10. Como host na TV, quero o botão de encerrar sessão disponível na tela final, para limpar a partida quando a noite acabar.
11. Como host na TV, quero que `SHOW_1` e `SHOW_2` continuem mostrando a grade de filmes votados, para entender por que ainda não houve consenso antes da próxima rodada.
12. Como jogador no celular, quero ver o poster real dos filmes na minha tela de resultado, para reconhecer os títulos sem depender só do texto.
13. Como host numa rede local sem internet, quero que os posters da tela final carreguem do disco, para que a revelação funcione em qualquer ambiente de "noite de filme".
14. Como host, quando um filme de consenso não tiver poster resolvido, quero que a tela ainda funcione com um placeholder, para nunca ver um card quebrado na hora da revelação.
15. Como desenvolvedor, quero que o algoritmo de match (`match.py`) permaneça puro (somente votos), para que a injeção de poster/ano não acople o cálculo ao manifesto.
16. Como desenvolvedor, quero um único ponto de enriquecimento que adiciona poster local e ano a um resultado de match, reutilizado pela TV e pelo celular, para não duplicar a lógica.
17. Como desenvolvedor, quero que o estado `FINAL` exponha ao template a lista de filmes de consenso (apenas `is_match`), para a TV destacar exatamente os títulos que convergiram.
18. Como avaliador do TCC, quero a tela final consistente com o design V3 em qualquer demonstração, para que a qualidade percebida do projeto seja alta.

## Implementation Decisions

### Módulos modificados

- **Template da TV (`templates/desktop/lobby.html`):** o ramo único que hoje cobre `SHOW_1`/`SHOW_2`/`FINAL` é dividido. Um novo ramo `FINAL` renderiza o layout do Figma (coluna de info à esquerda + área de posters de consenso); o ramo existente (grade de filmes votados) passa a cobrir apenas `SHOW_1`/`SHOW_2`.
- **Rota da TV (`routes/desktop.py`):** no estado `FINAL`, além do `match_data` enriquecido, expõe ao contexto a lista `consensus_movies` = filmes com `is_match == True`. Mantém `result_seconds` (cartão de tempo) e `players` (avatares), já disponíveis.
- **Enriquecimento compartilhado (`routes/game.py`):** uma função única (`enrich_match_movies`) injeta, em cada filme do resultado de match, o **caminho local do poster** (a partir do `_manifest`) e o **ano** (a partir de `MOVIE_LOOKUP`). Usada tanto pela rota mobile de `/results` quanto pela rota `/desktop`. Filmes sem poster no manifesto ficam sem o campo `poster` — o placeholder de gradiente cobre.
- **`match.py`:** permanece **inalterado e puro** (só agrega votos). A dependência do manifesto vive no enriquecimento, não no cálculo.
- **CSS (`static/css/main.css`):** novas classes para o layout final da TV — cartão de tempo (rótulo + `MM:SS`), poster herói (1 filme) e fileira de posters (N filhmes), linha de avatares. O placeholder de gradiente reaproveita o padrão já usado no deck/grade.

### Pré-requisito (build-time, fora desta tela)

- O **manifesto de posters** (`data/posters.json`) e as imagens em `static/img/posters/` precisam estar populados pelo resolvedor (`resolve_posters.py`, PRD `docs/prd-posters.md`). É pré-requisito tanto da tela final quanto do jogo inteiro (o serving de catálogo já filtra por manifesto). A execução do resolvedor é um passo de build, não parte desta mudança de UI.

### Layout de consenso (decisão de design travada)

- **1 filme de consenso:** poster grande/centralizado (herói do Figma), com título.
- **N filmes de consenso (≥2):** fileira de posters menores, cada um com seu título embaixo. A coluna singular "FILME ESCOLHIDO" do mockup é removida.
- Coluna de info à esquerda (RESULTADO COLETIVO + frase + cartão de tempo + avatares) é constante, independente da quantidade.

### Contratos / formatos

- Cada filme em `match_data["movies"]` ganha, após o enriquecimento: `poster` (caminho local, ex.: `static/img/posters/<id>.jpg`; **ausente** se não houver no manifesto) e `year` (de `MOVIE_LOOKUP`, quando existir). Os campos pré-existentes (`movie_id`, `movie_title`, `category`, `players`, `is_match`, `count`) não mudam.
- `consensus_movies` (contexto do template no `FINAL`): sublista de `match_data["movies"]` com `is_match == True`, já ordenada por contagem decrescente (herda a ordenação de `calculate_match`).
- Caminho do poster no HTML segue o padrão já usado em `round.js`: `"/" + poster` → `/static/img/posters/<id>.jpg`.

### Decisões arquiteturais

- Separação de estado no template em vez de um layout único parametrizado: `FINAL` é conceitualmente uma tela diferente, não uma variação da grade.
- Enriquecimento de poster centralizado em um ponto (`routes/game.py`), ao lado do `_manifest`, em vez de espalhar lookups por rota/template.
- Reuso do placeholder de gradiente existente como rede de segurança para filmes sem poster — nenhuma tela quebra por poster faltante.

## Testing Decisions

Bons testes aqui validam **comportamento externo** — o que a rota `/desktop` renderiza em cada estado — e **não** detalhes de implementação (nomes de classes CSS, estrutura interna de helpers). Segue o padrão "slice" do projeto: app Flask com DB in-memory via fixtures de `conftest.py`, `test_client`, e o **manifesto injetado por `monkeypatch`** (mesmo padrão de `tests/test_slice3_local_poster.py`: `monkeypatch.setattr(gm, "_manifest", FAKE_MANIFEST)`).

Seams testados (preferindo o mais alto, `GET /desktop`):

1. **`GET /desktop` no estado `FINAL` (seam mais alto):** com votos que produzem consenso e um manifesto de teste injetado, a resposta deve (a) destacar **apenas** os filmes de consenso (`is_match`), (b) incluir o **caminho local do poster** desses filmes, (c) renderizar o **cartão de tempo** a partir de `result_seconds` e (d) renderizar os **avatares** dos participantes. Prior art: `tests/test_slice4_round_timer.py`, `tests/test_slice5_submit_white.py` (GET/POST em rota + asserção na resposta).
2. **`GET /desktop` com 1 vs. N filmes de consenso:** um cenário com um único filme de consenso e outro com dois, assegurando que ambos os títulos de consenso aparecem na resposta quando há vários (a "fileira" não esconde nenhum).
3. **`GET /desktop` nos estados `SHOW_1`/`SHOW_2`:** continuam renderizando a grade de filmes votados (regressão — o split de template não muda as telas intermediárias).
4. **Enriquecimento de poster/ano (via seam de rota):** com manifesto injetado, os filmes do resultado carregam `poster` quando presentes no manifesto e **não** carregam quando ausentes (placeholder). Testado pela resposta da rota, não pela função isolada, para validar o comportamento observável. Prior art: `tests/test_slice3_local_poster.py` (injeção de `_manifest`, asserção no payload servido).

Fora do teste unitário: a rede real do TMDB e o download de imagens (cobertos pelo PRD de posters, mockados na fronteira lá), e a aparência pixel-a-pixel do CSS (validação visual manual contra o Figma).

## Out of Scope

- **Redesenho visual V3 da tela de resultado mobile** (`results.html`): nesta entrega o mobile apenas herda o poster real via enriquecimento compartilhado; o seu layout V3 é trabalho separado.
- **Popular o manifesto de posters**: a execução do `resolve_posters.py`, a revisão da `review_list.json` e a decisão de piso por categoria pertencem ao PRD `docs/prd-posters.md`.
- **Sinopse e rating reais**: continuam derivados deterministicamente do hash do id em `round.js`.
- **Mudanças no algoritmo de match de votos, máquina de estados, avatares ou integração Arduino.**
- **Animações/transições de revelação** (ex.: poster surgindo): a tela final é estática nesta entrega; motion fica para depois.

## Further Notes

- O Figma mostra a coluna singular "FILME ESCOLHIDO" porque o mockup assume **um** vencedor; o requisito do produto admite **múltiplos** filmes de consenso, então essa coluna é substituída pela fileira de posters com títulos. Decisão travada com o usuário durante a entrevista.
- A tela final é o pré-requisito de poster mais visível: se o manifesto estiver vazio, o jogo sequer serve filmes nas rodadas (o serving filtra por manifesto). Logo, popular o manifesto é condição para qualquer demonstração — não só para esta tela.
- `match.py` é mantido puro de propósito: o cálculo de match já tem testes e não deve passar a depender de IO de manifesto.
- Publicação no GitHub (`bytols/TCC`) via `docs/issues/publish.sh` requer `gh auth login`; enquanto não houver tracker/auth, este PRD permanece como arquivo, como o `docs/prd-posters.md`.
