# UI — Remoção do Check de Seleção e Ajuste de Espaçamento na Tela de Filmes

## Problem Statement

Na tela de seleção de filmes (deck cíclico, rounds 1/2/3), um ícone de check (✓) circular aparece no canto superior direito de cada card. Usuários confundem esse elemento com um botão clicável e tentam interagir com ele, gerando fricção. O feedback de seleção já existe em dois canais redundantes: o destaque visual do card (`in-list` → borda/glow branco) e o texto do botão externo que muda para "✓ ADICIONADO". O check no card é ruído visual, não sinal.

Além disso, os dois botões do rodapé do deck ("ADICIONAR À MINHA LISTA" e "PRÓXIMO") não têm espaçamento entre si, fazendo-os parecer um único bloco e aumentando o risco de toque acidental no botão errado.

## Solution

Remover o elemento `.deck-check` do DOM e do CSS, eliminando completamente o check do card. Aumentar o espaçamento vertical entre os dois botões do rodapé do deck para `0.75rem`, tornando-os claramente distintos sem alterar a hierarquia visual.

## User Stories

1. Como jogador mobile, quero que o card de filme selecionado mostre claramente que está na minha lista, sem elementos que pareçam botões extras, para que eu entenda de imediato o feedback e não me confunda.
2. Como jogador mobile, quero que o botão "ADICIONAR" e o botão "PRÓXIMO" estejam visivelmente separados, para que eu não toque no errado por acidente.
3. Como jogador mobile, quero que a única ação explícita de adicionar/remover um filme seja o botão externo ao card, para que o modelo mental de interação seja simples e consistente.

## Implementation Decisions

- **Remoção do `.deck-check`**: o elemento `<div class="deck-check">✓</div>` é removido da função de criação de cards em `round.js`. Os dois blocos CSS (estado padrão e estado `in-list`) são removidos de `main.css`. Nenhum substituto visual é introduzido — o card já comunica seleção pelo estilo `.in-list` (borda e glow brancos no poster).
- **Espaçamento dos botões**: `margin-top: 0.75rem` adicionado ao `.btn-submit` quando dentro de `.deck-footer` (seletor `.deck-footer .btn-submit`), mantendo o ajuste localizado e sem afetar o `.btn-submit` do rodapé fixo de outras telas.
- Nenhuma mudança em lógica de estado, eventos ou templates HTML.

## Testing Decisions

Mudanças puramente visuais/estruturais de DOM e CSS — não há lógica de negócio nova. Testes unitários/de integração não são aplicáveis aqui. A validação correta é visual: abrir o deck em um dispositivo real ou via browser DevTools (viewport mobile 430px) e confirmar:

- Nenhum círculo de check aparece nos cards (selecionados ou não).
- O card selecionado continua exibindo o destaque branco (`.in-list`) no poster.
- O botão "ADICIONAR" e "PRÓXIMO" têm espaço visivelmente distinto entre si.
- Clicar em qualquer região do card (exceto arrastar) abre o modal de detalhes, não aciona seleção.

## Out of Scope

- Redesign do mecanismo de feedback de seleção (brilho, cor, animação do card).
- Alterações no modal de detalhes ou nos botões do modal.
- Espaçamento de botões em outras telas (gêneros, espera, resultados).
- Acessibilidade/ARIA (state de seleção para leitores de tela).

## Further Notes

A implementação foi aplicada diretamente: `round.js` e `main.css` já refletem essas mudanças. Issue movida para `done/` sem passar pelo ciclo AFK pois as alterações são triviais e foram co-decididas sincronamente com o usuário.
