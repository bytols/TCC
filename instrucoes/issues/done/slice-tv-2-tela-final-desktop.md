# Slice TV 2 — Reconstrução da tela final desktop (3 zonas + CSS do Figma)

> Status: ready-for-agent
> Tipo: HITL (revisão de design contra o Figma)

## Parent

`instrucoes/issues/correcoes-pos-teste-ruido.md`

## What to build

A tela final de consenso no desktop está quebrada: a marcação existe, mas as classes CSS correspondentes nunca foram escritas, então tudo renderiza com defaults do browser e fica totalmente diferente do Figma.

Esta slice **reestrutura a marcação para o layout de 3 zonas do Figma** (node `254-5321` do arquivo `1ea5BjwNJjsAWMgq430V00`) e **escreve o CSS faltante**:

- **Zona esquerda:** "RESULTADO COLETIVO" + subtítulo, card de **TEMPO** (duração da sessão) e linha de **avatares** dos jogadores.
- **Zona central:** posters do(s) filme(s) de consenso. Com mais de um filme, exibir **todos do mesmo tamanho em linha** (sem herói central); com um único filme, um poster.
- **Zona direita:** "FILME ESCOLHIDO" + título + metadados (ano · gênero).
- **Rodapé:** tagline + wordmark RUÍDO; barra de gradiente no topo.

A ação **ENCERRAR SESSÃO** permanece acessível na tela final. Medidas, cores e espaçamentos devem ser extraídos do Figma (via `get_design_context` do node) e mapeados aos tokens existentes do design system.

## Acceptance criteria

- [ ] A tela final renderiza as 3 zonas (esquerda: título+subtítulo+TEMPO+avatares; centro: posters; direita: FILME ESCOLHIDO+título+meta) sem elementos sobrepostos ou fora do fluxo em telas grandes.
- [ ] Card de TEMPO mostra a duração da sessão; avatares dos jogadores aparecem.
- [ ] Consenso com múltiplos filmes mostra posters em linha, todos do mesmo tamanho; com um filme, um poster. Placeholder consistente quando não há poster.
- [ ] Zona direita mostra título e metadados (ano · gênero) do filme escolhido.
- [ ] Tagline e wordmark no rodapé; ação ENCERRAR SESSÃO funcional.
- [ ] Layout fiel ao Figma `254-5321` (revisão de design humana).
- [ ] Teste de renderização via `GET /desktop` no estado `FINAL` (manifesto injetado) confirma as zonas e os posters reais, seguindo `tests/test_slice_final_tv_layout.py` e `test_slice_final_time_avatars.py`.

## Blocked by

None - can start immediately

> Nota: edita os mesmos arquivos da slice "Posters SHOW_1/SHOW_2" — recomenda-se fazer aquela antes para reduzir conflito.
