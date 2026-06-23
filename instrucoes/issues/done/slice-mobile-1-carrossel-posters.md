# Slice Mobile 1 — Posters visíveis no carrossel (corrige colapso de layout)

> Status: ready-for-agent

## Parent

`instrucoes/issues/correcoes-pos-teste-ruido.md`

## What to build

No mobile, os posters não aparecem no carrossel (deck estilo Tinder) — só surgem quando o jogador toca no filme e o modal full-screen abre. A causa é **colapso de layout**: o card do deck depende de `aspect-ratio` dentro de um container flexível que pode colapsar a altura no mobile, deixando o elemento de poster com altura zero (background invisível). Não é lazy-load nem CORS — o path está correto (o modal usa o mesmo e funciona).

Esta slice dá **altura concreta** ao palco do deck e um **fallback de altura** ao card (independente de `aspect-ratio`), garantindo que o `background-size: cover` tenha área para pintar. Vale para rounds 1, 2 e 3 (mesmo componente).

## Acceptance criteria

- [ ] No carrossel mobile, o poster do filme aparece no card central sem precisar tocar.
- [ ] Os cards vizinhos do deck também mostram seus posters.
- [ ] Os posters aparecem mesmo quando `aspect-ratio` não é respeitado (fallback de altura), sem cards vazios.
- [ ] Comportamento consistente nos rounds 1, 2 e 3.
- [ ] Validação em viewport mobile (incl. Safari iOS) confirma os posters renderizando.

## Blocked by

None - can start immediately
