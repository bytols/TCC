# Slice 3 — Frontend lê poster local; remove fetch ao vivo

> Type: AFK · Triage: ready-for-agent

## Parent

PRD: `docs/prd-posters.md` — "Lista de filmes só com poster verificado (RUÍDO)".

## What to build

Trocar a busca de poster ao vivo pelo caminho local já embutido no payload, eliminando flicker e dependência de internet durante a partida.

- `round.js` lê `m.poster` direto do payload e aplica no card do deck e no fundo desfocado do modal de detalhes, sem fetch assíncrono.
- Remove a rota `/api/poster/<movie_id>` e o caminho de fetch lazy em runtime; `posters.py` passa a ser utilitário do script de build, não dependência de runtime.
- O placeholder de gradiente permanece no código como rede de segurança morta (não deve disparar para filmes do catálogo).

Resultado demoável: abrir o deck mostra o poster real imediatamente (sem o flash cinza), o modal usa o poster real desfocado de fundo, e tudo funciona numa LAN sem internet.

## Acceptance criteria

- [ ] Cards do deck exibem o poster local imediatamente, sem chamada a `/api/poster`.
- [ ] O fundo desfocado do modal de detalhes usa o poster real do filme.
- [ ] A rota `/api/poster` e o fetch lazy em runtime foram removidos.
- [ ] Com os posters em disco, o jogo carrega as capas sem internet (somente LAN).
- [ ] O placeholder de gradiente continua presente no código, mas não dispara para filmes do catálogo.

## Blocked by

- Slice 2 (Catálogo servido só com filmes verificados) — depende do campo `poster` no payload.
