# Slice Mobile 2 — Performance: app fluido e responsivo no mobile

> Status: ready-for-agent
> Tipo: HITL (validação manual em iPhone/Safari real)

## Parent

`instrucoes/issues/correcoes-pos-teste-ruido.md`

## What to build

No mobile a aplicação trava e fica pouco responsiva em todas as telas — desde o primeiro botão "INICIAR" até o fim. A causa principal é um custo sempre-ativo: a camada de glow anima um **blur de raio grande (95–105px) em tela cheia, infinitamente**, e há muitos elementos empilhando `backdrop-filter: blur()` sobre essa superfície borrada em movimento — combinação cara para a GPU mobile, presente em todas as telas.

Esta slice ataca o custo de forma sistêmica, preservando a estética:

- Parar de animar o blur: pré-borrar o blob e animar apenas `transform`, ou desligar a animação no mobile (media query de ponteiro coarse) e reduzir o raio do blur.
- Reduzir o raio do `--glass-blur` no mobile e remover `backdrop-filter` de elementos que rolam (cards de lista), usando fundo translúcido sólido como fallback.
- No deck, montar/decodificar apenas os cards visíveis (não o catálogo inteiro), usando atributos de decodificação e `content-visibility` para os fora de tela.
- Revisar listeners de gesto / `requestAnimationFrame` do deck para evitar acúmulo.

## Acceptance criteria

- [ ] A tela inicial e o botão INICIAR respondem imediatamente ao toque.
- [ ] Rolagem e toques são fluidos em todas as telas do mobile (lobby, join, rounds, resultados).
- [ ] O carrossel desliza suavemente, sem travar.
- [ ] A camada de glow não anima blur de raio grande no mobile; `backdrop-filter` reduzido/removido onde causa repaint em scroll.
- [ ] O deck não monta/decodifica o catálogo inteiro de uma vez.
- [ ] Validação manual em iPhone/Safari real confirma a fluidez (incl. paridade com outros aparelhos).

## Blocked by

- `instrucoes/issues/slice-mobile-1-carrossel-posters.md` (ambas mexem no deck; a virtualização parte de um deck que já renderiza posters corretamente)
