# Slice Avatar 1 — Correção de bugs do construtor de personagem

> Status: ready-for-agent

## Parent

`instrucoes/issues/correcoes-pos-teste-ruido.md`

## What to build

O construtor de avatar apresenta bugs de estado: a seleção pode se perder ao alternar entre as abas de personalização, e nem toda mudança de opção é refletida no preview SVG ao vivo.

Esta slice corrige o comportamento, sem adicionar opções novas:

- A seleção de cada categoria é **preservada ao alternar entre abas**.
- **Toda mudança de opção atualiza imediatamente** o preview do avatar.
- A escolha final **persiste durante a sessão** (via `character_json`), refletindo nas telas seguintes.

## Acceptance criteria

- [ ] Trocar de aba e voltar mantém todas as seleções já feitas.
- [ ] Selecionar qualquer opção (rosto, cabelo, pele, cor do cabelo, acessório, fundo) atualiza o preview na hora.
- [ ] Ao entrar na sessão, o avatar gerado corresponde às escolhas feitas, e a identidade persiste nas telas seguintes (waiting/resultados).
- [ ] Feedback visual de seleção (item ativo) funciona corretamente em todas as categorias.

## Blocked by

None - can start immediately
