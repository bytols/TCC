# Slice 1 — Limite de 4 jogadores

## Parent

PRD: [auto-start-player-cap.md](auto-start-player-cap.md)

## What to build

Reduzir o limite máximo de participantes de 10 para 4. A validação nas rotas de join (GET e POST) já existe e usa `config.MAX_PLAYERS` — basta alterar o valor. Nenhuma nova lógica de guarda é necessária.

O comportamento demoável: ao tentar entrar como 5º jogador, o usuário vê a tela `session_full`.

## Acceptance criteria

- [ ] `MAX_PLAYERS` vale 4 em produção
- [ ] `GET /join` com 4 jogadores já no lobby renderiza `session_full.html`
- [ ] `POST /join` com 4 jogadores já no lobby retorna 403 com `session_full.html`
- [ ] Os primeiros 4 jogadores conseguem entrar normalmente
- [ ] `CLAUDE.md` e qualquer outro comentário no código que mencione "10" como limite máximo estão atualizados

## Blocked by

None — can start immediately.
