# Slice TV 1 — Posters nas telas intermediárias de consenso (SHOW_1/SHOW_2)

> Status: ready-for-agent

## Parent

`instrucoes/issues/correcoes-pos-teste-ruido.md`

## What to build

As telas de resultado parcial na TV (rodada 1 e rodada 2) hoje ignoram o poster do filme e mostram um gradiente fixo + a inicial do título, mesmo o dado de poster já estando disponível no resultado enriquecido.

Esta slice faz essas telas renderizarem o **poster real** quando ele existe, usando o mesmo padrão da tela final (`has-poster` via `background-image` + `background-size: cover`), e mantendo um **placeholder consistente** (gradiente + inicial) quando o poster não existe.

## Acceptance criteria

- [ ] No estado `SHOW_1` e `SHOW_2`, cada card de filme exibe o poster real quando disponível.
- [ ] Quando não há poster, exibe o placeholder (gradiente + inicial) sem quebrar o layout.
- [ ] A regra CSS garante `background-size: cover` para os posters dessas telas.
- [ ] Teste de renderização via `GET /desktop` com manifesto de posters injetado por monkeypatch confirma poster real quando presente e placeholder quando ausente, seguindo `tests/test_slice3_local_poster.py` e `test_slice_final_tv_layout.py`.

## Blocked by

None - can start immediately

> Nota: edita os mesmos arquivos da slice "Tela final desktop" (`templates/desktop/lobby.html`, `static/css/main.css`). Sem bloqueio rígido, mas recomenda-se fazer esta antes para reduzir conflito.
