# Slice 4 — Script de verificação de catálogo

> Type: AFK · Triage: ready-for-agent

## Parent

PRD: `docs/prd-posters.md` — "Lista de filmes só com poster verificado (RUÍDO)".

## What to build

Uma ferramenta de verificação que dá sinal ao desenvolvedor quando um filme do catálogo não tem poster no manifesto (e portanto está sendo silenciosamente escondido do jogo).

- Função pura sobre `(catálogo, manifesto)` que devolve os ids presentes em `data/movies.py` mas ausentes de `data/posters.json`.
- CLI fino que imprime a lista de filmes sem poster verificado.

Complementa o enforcement silencioso do serving (Slice 2): adicionar um filme novo sem rodar o resolvedor não o faz aparecer, e este script revela exatamente quais.

## Acceptance criteria

- [x] Função pura retorna os ids do catálogo ausentes do manifesto, sem IO.
- [x] CLI imprime a lista de filmes sem poster verificado.
- [x] Teste unitário da função pura com catálogo e manifesto fabricados (sem IO).

## Implementação

- `verify_catalog.py`: `missing_posters(catalog, manifest)` pura + CLI com `--manifest` opcional; exit 1 se há filmes faltando.
- `tests/test_verify_catalog.py`: 5 testes TDD (tracer bullet, all-covered, partial, extra keys, return type).
- 59/59 testes passando, sem regressões.

## Blocked by

- Slice 1 (Resolvedor de posters) — precisa do formato do manifesto `data/posters.json`.
