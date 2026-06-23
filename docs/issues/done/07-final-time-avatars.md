# Slice 2b — Tela FINAL na TV: cartão de tempo + avatares dos participantes

> Type: AFK · Triage: ready-for-agent

## Parent

PRD: `docs/prd-final-screen.md` — "Revisão visual da tela de resultado final / consenso (RUÍDO)".

## What to build

Completa a coluna de informação à esquerda da tela final na TV, fechando a fidelidade ao Figma V3 (frame "FIM", node `254:5321`). Sobre o esqueleto entregue no slice 2a, adiciona:

- Um **cartão de tempo** destacado: o rótulo "TEMPO" sobre o tempo total da experiência em formato `MM:SS`, derivado de `result_seconds` (já disponível no contexto da rota no estado `FINAL`).
- A **linha de avatares** dos participantes, a partir de `players` (já disponível no contexto), reforçando quem participou da decisão coletiva.

Ambos seguem o glassmorphism e os tokens do design system V3 já usados nas demais telas.

## Acceptance criteria

- [ ] `GET /desktop` no estado `FINAL` renderiza o cartão de tempo com o rótulo "TEMPO" e o tempo total formatado como `MM:SS` a partir de `result_seconds`.
- [ ] Quando `result_seconds` não estiver disponível, a tela não quebra (cartão de tempo é omitido ou neutro).
- [ ] `GET /desktop` no estado `FINAL` renderiza um avatar para cada participante (`players`).
- [ ] O cartão de tempo e a linha de avatares ficam na coluna de informação à esquerda, coerentes com o layout do slice 2a.
- [ ] Teste via `GET /desktop` (manifesto injetado): a resposta contém o tempo formatado e um avatar por participante adicionado à sessão.

## Blocked by

- Slice 2a — Tela FINAL na TV: split de template + posters de consenso (`06-final-tv-layout.md`)
