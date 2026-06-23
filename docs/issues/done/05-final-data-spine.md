# Slice 1 — Tela final: poster/ano no resultado + `consensus_movies` no FINAL

> Type: AFK · Triage: ready-for-agent

## Parent

PRD: `docs/prd-final-screen.md` — "Revisão visual da tela de resultado final / consenso (RUÍDO)".

## What to build

A spine de dados que alimenta a tela final, sem ainda mexer no layout. Um ponto único de enriquecimento adiciona, a cada filme de um resultado de match, o **caminho local do poster** (a partir do manifesto `data/posters.json`) e o **ano** (a partir de `MOVIE_LOOKUP`). O algoritmo de match continua **puro** (só agrega votos) — a dependência do manifesto vive no enriquecimento, não no cálculo.

Tanto a rota de resultado mobile (`/results`) quanto a da TV (`/desktop`) passam o resultado por esse enriquecimento. No estado `FINAL`, a rota da TV expõe ao template a lista `consensus_movies` = apenas os filmes com `is_match == True` (já ordenada por contagem decrescente, herdada do cálculo de match).

Filmes sem poster no manifesto simplesmente ficam sem o campo `poster` — o placeholder de gradiente existente cobre, sem quebrar nada. Como efeito colateral, os itens da tela de resultado mobile passam a herdar o poster real (o redesenho visual do mobile é outro trabalho).

## Acceptance criteria

- [ ] `GET /desktop` no estado `FINAL` (com manifesto injetado nos testes) entrega cada filme do resultado com o campo `poster` quando o id está no manifesto, e sem `poster` quando não está.
- [ ] `GET /desktop` no estado `FINAL` expõe `consensus_movies` contendo **apenas** filmes com `is_match == True`, na ordem de contagem decrescente.
- [ ] `GET /results` (mobile) também passa pelo mesmo enriquecimento: itens com id no manifesto carregam `poster`.
- [ ] O cálculo de match permanece puro: nenhuma dependência de manifesto/IO no módulo de match (verificável por não regredir os testes de match existentes).
- [ ] O campo `year` é injetado a partir de `MOVIE_LOOKUP` quando disponível.
- [ ] Testes via seam de rota com `_manifest` injetado por `monkeypatch` (padrão de `tests/test_slice3_local_poster.py`); sem dependência do `data/posters.json` real.

## Blocked by

- None — can start immediately.

> Nota: a **verificação visual** com posters reais depende de `data/posters.json` populado (PRD `docs/prd-posters.md`). Os testes deste slice não dependem disso (manifesto injetado).
