# PRD — Bug: posters não aparecem no carrossel até interação

> Status: resolvido
> Data: 2026-06-23
> Telas afetadas: carrossel mobile (rounds 1/2/3), resultado mobile (`/results`), resultado intermediário desktop (SHOW_1/SHOW_2)

## 1. Resumo

Os pôsteres dos filmes não apareciam no carrossel estilo Tinder do mobile. O card
ficava escuro, **sem a letra inicial e sem a imagem** — e o pôster só "surgia"
quando o jogador arrastava/clicava para navegar entre os cards. As telas de
resultado (mobile e desktop) também não mostravam pôsteres.

A causa raiz **não era** lazy-load, CORS, path errado, arquivo ausente nem
colapso de layout (`aspect-ratio` / altura zero) — todas hipóteses levantadas
antes e descartadas pela investigação. A causa real:

> **O deck era montado (com as `background-image` atribuídas) enquanto o
> container `#phase-movies` ainda estava em `display:none`. Navegadores não
> carregam/pintam imagens de fundo de elementos numa subárvore `display:none`.
> Quando a fase ficava visível, os cards já montados não repintavam — só uma
> navegação (que reatribui o `innerHTML` de um slot) forçava o novo layout a
> setar a `background-image` com o elemento já visível.**

## 2. Sintoma observado

- Card central do carrossel: retângulo escuro, sem letra inicial, sem pôster.
- Importante: a **ausência da letra inicial** é o que aponta o diagnóstico. Em
  `round.js`, quando `m.poster` é verdadeiro, a classe `has-poster` é aplicada
  (e `.deck-poster.has-poster .deck-initial { display:none }` esconde a letra).
  Logo, o dado *tinha* pôster e a classe *foi* aplicada — só a imagem não pintou.
- Ao arrastar/tocar num card lateral, o pôster aparecia.

## 3. Como foi diagnosticado (e o que foi descartado)

Trilha de evidências, em ordem:

1. **Arquivos existem e são válidos** — `data/posters.json` tem 203 entradas;
   os `.jpg` em `static/img/posters/` são JPEG reais 500×750 (`file` confirmou).
   → descarta "arquivo ausente / corrompido".
2. **Servidor serve as imagens** — `curl` em
   `/static/img/posters/<id>.jpg` → `HTTP 200 image/jpeg`. → descarta 404 / path
   errado / problema de static serving. (Atenção: a porta real é **5001**, não
   5000 como diz o CLAUDE.md — o primeiro `curl` em :5000 deu `HTTP 000` e quase
   mandou a investigação para o lado errado.)
3. **O dado chega correto ao browser** — dirigindo o jogo via `curl`
   (criar players → `/admin/start` → `/round/1`), o `<script id="movies-data">`
   já continha `"poster": "static/img/posters/..."` para cada filme.
   → descarta "backend não injeta pôster".
4. **Logo, sobra o front** — com dados certos, classe certa e imagem servível, o
   único ponto que explicava "só pinta após interação" era o ciclo de vida do
   `background-image` sob `display:none`.

**Hipótese anterior incorreta:** a slice `slice-mobile-1-carrossel-posters.md`
atribuiu o bug a colapso de layout / altura zero por `aspect-ratio`. Isso não se
sustentou: o card tinha tamanho visível na tela (a borda/glow apareciam), e o
pôster pintava após navegar sem qualquer mudança de altura.

## 4. Causa raiz (detalhe técnico)

Em `static/js/round.js`, `showMoviePhase()` (round 1) fazia:

```js
buildDeck(cats);                       // monta os cards + seta background-image
phaseMovies.style.display = 'flex';    // só agora torna visível
```

`buildDeck()` → `layout()` escreve `innerHTML` com
`style="background-image:url(...)"`. Como isso roda com a subárvore ainda
`display:none`, o navegador **não busca nem pinta** a imagem de fundo. Ao
tornar visível depois, os cards já existentes não são reprocessados (o
`layout()` só reescreve o `innerHTML` de um slot quando o item daquele slot
muda — `if (card.dataset.id !== m.id)`). Por isso só uma **navegação** trazia a
imagem.

Rounds 2/3 não sofriam (o deck já nasce visível no `init()`), o que reforçou o
diagnóstico: o único caso quebrado era o que montava o deck oculto.

## 5. Correção aplicada

- **`static/js/round.js`** — inverter a ordem em `showMoviePhase()`: **tornar a
  fase visível primeiro, montar o deck depois**, para que as `background-image`
  sejam atribuídas com os elementos já no fluxo visível.

- **`templates/mobile/results.html`** — `your-pick-poster` passou a renderizar a
  imagem real (`movie_entry.poster`, já enriquecido por `enrich_match_movies`),
  com fallback para a letra inicial quando não há pôster.

- **`templates/desktop/lobby.html`** — os cards do resultado **intermediário**
  (SHOW_1/SHOW_2, bloco `result-movie-card`) passaram a usar `has-poster` +
  `background-image`, espelhando o que a tela FINAL já fazia. (Este era um
  template separado, não coberto pelos fixes anteriores.)

- **`static/css/main.css`** — regras `.has-poster` (`background-size: cover;
  background-position: center;` + `overflow: hidden`) para `.your-pick-poster` e
  `.result-movie-poster`.

## 6. Critérios de aceite

- [x] Carrossel mobile mostra o pôster do card central sem precisar tocar.
- [x] Cards vizinhos do deck também mostram seus pôsteres.
- [x] Rounds 1, 2 e 3 consistentes.
- [x] Resultado mobile (`/results`) mostra os pôsteres dos filmes escolhidos.
- [x] Resultado intermediário desktop (SHOW_1/SHOW_2) mostra os pôsteres.
- [x] Validado via HTML servido pelo servidor real (`curl`).

## 7. Lições para o futuro

1. **`display:none` não carrega `background-image`.** Ao montar conteúdo com
   imagens de fundo via JS, torne o container visível **antes** de setar os
   estilos — ou force um relayout/reatribuição depois de exibir.
2. **A ausência da letra de fallback é um sinal de diagnóstico**, não só estética:
   significava que a classe `has-poster` foi aplicada e o problema era só a
   pintura da imagem, não o dado.
3. **Confirme a porta real (5001)** antes de concluir "servidor não responde".
4. **O mesmo conceito visual vive em 3 templates diferentes** (carrossel,
   resultado mobile, resultado desktop FINAL e SHOW). Corrigir um não corrige os
   outros — varra os três ao mexer em pôster.
5. **JS estático é cacheado pelo navegador.** Depois de corrigir `round.js`, é
   preciso hard-refresh no celular; os templates recarregam sozinhos via
   `TEMPLATES_AUTO_RELOAD`, o `.js` não.
