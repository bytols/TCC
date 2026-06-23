# Slice 2 — Catálogo servido só com filmes verificados + poster embutido

> Type: AFK · Triage: ready-for-agent

## Parent

PRD: `docs/prd-posters.md` — "Lista de filmes só com poster verificado (RUÍDO)".

## What to build

Um ponto único de serving do catálogo que garante que **só filmes com poster verificado** cheguem ao jogo, com o caminho local do poster já embutido no payload.

- Carrega o manifesto `data/posters.json` (carga injetável, para os testes trocarem por um manifesto falso).
- Filtra `MOVIES` para conter apenas ids presentes no manifesto e injeta um campo `poster` (caminho local) em cada dict de filme, antes de serializar para `#movies-data` na rodada 1.
- Rodadas 2/3 herdam automaticamente: o `RoundPool` é construído a partir dos votos da rodada 1 (já filtrados); `pool_grouped` apenas carrega o `poster` adiante.

Verificável de ponta a ponta via `GET /round/1`: o payload não contém nenhum id órfão (ausente do manifesto) e todo filme servido traz um `poster`.

## Acceptance criteria

- [ ] `GET /round/1` serializa em `#movies-data` apenas filmes presentes no manifesto.
- [ ] Todo filme no payload servido tem um campo `poster` com caminho local.
- [ ] Filmes órfãos (no `movies.py` mas ausentes do manifesto) não aparecem em nenhuma rodada, incluindo o pool de 2/3.
- [ ] Teste via `GET /round/1` com manifesto falso injetado: exclui ids órfãos e inclui `poster` em todo filme servido (padrão slice de `tests/`).
- [ ] A carga do manifesto é injetável, permitindo o teste sem o arquivo real de 300 entradas.

## Blocked by

- Slice 1 (Resolvedor de posters) — precisa do manifesto real para o jogo ter filmes; os testes usam manifesto falso injetado.
