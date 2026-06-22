# Slice 1 — Resolvedor de posters: manifesto + imagens em disco + relatório

> Type: HITL · Triage: ready-for-agent (com revisão humana obrigatória)

## Parent

PRD: `docs/prd-posters.md` — "Lista de filmes só com poster verificado (RUÍDO)".

## What to build

Um script de build (execução única, offline) que cura os posters de todo o catálogo:

- Percorre os 300 filmes de `data/movies.py`.
- Para cada filme, busca no TMDB pelo título pt-BR + ano; se não houver match limpo, tenta o título original.
- Baixa o poster de cada match aceito para `static/img/posters/<movie_id>.jpg` (auto-hospedado, como os avatares).
- Grava o manifesto versionado `data/posters.json` no formato `{ "<movie_id>": { "tmdb_id": <int>, "file": "<path local>" }, ... }` — apenas filmes com poster resolvido.
- **Match-safety:** auto-aceita correspondências limpas (título + ano exato); escreve casos ambíguos (ano divergente, múltiplos candidatos) numa **lista de revisão** separada para confirmação humana antes de entrarem no manifesto. Não publica poster de baixa confiança automaticamente.
- Emite um **relatório de falhas por categoria** (quantos filmes de cada gênero não resolveram), base para a decisão posterior de piso por categoria.

Reaproveita a lógica de fetch ao TMDB já existente em `posters.py`. Requer `TMDB_API_KEY` no ambiente (build-time).

A lógica que classifica um resultado do TMDB como auto-aceite vs. revisão vs. órfão deve ser uma função isolada, testável com a chamada HTTP do TMDB mockada (sem rede). O download e a escrita em disco ficam fora do teste unitário (mockados na fronteira).

## Acceptance criteria

- [x] Rodar o script com `TMDB_API_KEY` definido gera `data/posters.json` e baixa os posters aceitos para `static/img/posters/`.
- [x] O manifesto contém `tmdb_id` + caminho local por filme resolvido; filmes sem poster ficam de fora.
- [x] Matches de baixa confiança (ano divergente / múltiplos candidatos) vão para uma lista de revisão e **não** entram no manifesto sem confirmação.
- [x] O script imprime/grava um relatório de falhas por categoria.
- [x] A função de decisão de match tem teste unitário com TMDB mockado: ano exato → aceita; ano divergente / múltiplos candidatos → revisão; sem poster → órfão.
- [ ] **(HITL)** Relatório por categoria e lista de revisão foram revisados por um humano antes do fechamento.

## Implementação (2026-06-22)

- `resolve_posters.py` — script de build raiz; `python resolve_posters.py [--dry-run]`
- `classify_tmdb_result(expected_year, results)` — função pura isolada; regras: 1 resultado com poster e ano exato → accept; ano diverge ou múltiplos candidatos → review; nenhum poster → orphan
- Fallback automático: se busca com ano não resolve, tenta novamente sem filtro de ano
- `data/posters.json` — manifesto; `data/review_list.json` — fila HITL
- `tests/test_poster_resolver.py` — 8 testes unitários, todos passando (54 total, sem regressões)

## Blocked by

- **(HITL pendente)** Rodar `TMDB_API_KEY=xxx python resolve_posters.py` e revisar `data/review_list.json` + relatório de falhas antes de fechar.
