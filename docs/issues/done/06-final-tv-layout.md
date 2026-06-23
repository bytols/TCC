# Slice 2a — Tela FINAL na TV: split de template + posters de consenso

> Type: AFK · Triage: ready-for-agent

## Parent

PRD: `docs/prd-final-screen.md` — "Revisão visual da tela de resultado final / consenso (RUÍDO)".

## What to build

O esqueleto visual da tela final na TV, fiel ao Figma V3 (frame "FIM", node `254:5321`). Hoje o estado `FINAL` reaproveita o mesmo ramo de template das telas de resultado intermediário (`SHOW_1`/`SHOW_2`) — uma grade de todos os filmes votados. Este slice **separa** o `FINAL` num ramo próprio; a grade passa a cobrir apenas `SHOW_1`/`SHOW_2`.

O novo ramo `FINAL` renderiza:

- Título "RESULTADO COLETIVO" e a frase de fechamento "Depois de diferentes escolhas, o grupo chegou a um consenso."
- A **área de posters de consenso** (consumindo `consensus_movies`): quando há **um único** filme de consenso, ele aparece grande e centralizado (o "herói" do Figma) com o título; quando há **mais de um**, vira uma **fileira de posters** menores, cada um com seu título embaixo. A coluna singular "FILME ESCOLHIDO" do mockup é removida.
- Poster real de cada filme; se algum não tiver poster no manifesto, cai no placeholder de gradiente existente.
- Fundo no estado de consenso (verde) e o wordmark RUÍDO, como nas demais telas de TV.
- O botão de encerrar sessão.

O cartão de tempo e a linha de avatares ficam para o slice seguinte (2b).

## Acceptance criteria

- [ ] `GET /desktop` no estado `FINAL` renderiza um layout distinto do de `SHOW_1`/`SHOW_2` (não a grade de filmes votados).
- [ ] No `FINAL`, **apenas** os filmes de consenso (`is_match`) aparecem em destaque; filmes votados sem match não são listados como heróis.
- [ ] Com **1** filme de consenso, ele é renderizado como poster único/herói com título.
- [ ] Com **≥2** filmes de consenso, todos aparecem na fileira de posters, cada um com seu título (nenhum é escondido).
- [ ] O poster real é usado quando presente; ausência cai no placeholder de gradiente sem quebrar a tela.
- [ ] `SHOW_1`/`SHOW_2` continuam renderizando a grade de filmes votados (regressão).
- [ ] Botão de encerrar sessão presente no `FINAL`.
- [ ] Teste via `GET /desktop` (manifesto injetado): cenário com 1 consenso e cenário com 2 consensos, ambos com os títulos esperados presentes; mais um cenário `SHOW_1`/`SHOW_2` mantendo a grade.

## Blocked by

- Slice 1 — Tela final: poster/ano no resultado + `consensus_movies` no FINAL (`05-final-data-spine.md`)
