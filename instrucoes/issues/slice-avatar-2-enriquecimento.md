# Slice Avatar 2 — Enriquecimento visual do construtor (identidade RUÍDO)

> Status: aguardando-revisão-design
> Tipo: HITL (revisão de design)

## Parent

`instrucoes/issues/correcoes-pos-teste-ruido.md`

## What to build

Com os bugs do construtor já corrigidos, esta slice eleva a personalização visualmente, alinhando-a à identidade RUÍDO (glassmorphism, paleta azul → rosa → laranja, tema ruído → consenso). A criação de identidade deve virar parte da experiência, não uma tela crua.

- Estilizar abas e swatches conforme o design system (glass, espaçamento, tipografia uppercase).
- Feedback de seleção mais expressivo (glow/borda no item ativo).
- Preview do avatar maior e mais nítido.
- Opções novas de avatar apenas se necessárias para reforçar a identidade; o escopo visual exato é proposto e iterado com o desenvolvedor.

## Acceptance criteria

- [ ] Abas e swatches estilizados com o design system RUÍDO (glassmorphism + paleta), coerentes com as demais telas mobile.
- [ ] Item selecionado tem feedback visual claro (glow/borda).
- [ ] Preview do avatar maior e mais legível.
- [ ] Revisão de design humana aprova o resultado contra a identidade RUÍDO.
- [ ] Nenhuma regressão nos bugs já corrigidos (estado entre abas, preview ao vivo, persistência).

## Blocked by

- `instrucoes/issues/slice-avatar-1-bugfix.md` (o enriquecimento parte do construtor com estado já correto)

---

## O que foi implementado

**Bugfix retroativo (Slice Avatar 1 não estava completo):**
- `routes/join.py` GET agora passa `char_defaults=CHAR_DEFAULTS` ao template.
- `routes/join.py` POST extrai o character submetido antes das validações e o passa de volta (`char_defaults=character`) nos error re-renders.
- `templates/mobile/join.html` trocou `{% if loop.first %}` por `{% if opt.id == char_defaults[key] %}` em todos os radios/selected.

**Enriquecimento visual (Slice Avatar 2) — `static/css/main.css`:**
- Preview SVG: `124px → 160px`; `drop-shadow` no SVG para profundidade; wrapper com `border-bottom` separando preview das abas.
- Abas ativas: `background: rgba(255,255,255,0.07)` (glass tint) + `border-bottom` mais nítido.
- Swatches: `42px → 46px`; selecionado ganha anel duplo + glow difuso (`box-shadow: 0 0 0 3px … + 0 0 18px …`).
- Labels de swatch: uppercase, bold, tracking — alinhado à tipografia do design system.
- Chips de texto: padding e tracking aumentados; selecionado com glow de dois níveis (anel + blur).

**Testes — `tests/test_slice_avatar2_visual.py` (4 novos):**
- `test_join_renders_six_category_tabs` — 6 abas renderizadas.
- `test_join_color_options_render_as_swatches` — count de swatches bate com as opções de cor.
- `test_join_text_options_render_as_chips` — count de chips bate com as opções de texto.
- `test_join_avatar_preview_container_present` — container de preview está no DOM.

**Status dos testes:** 7 passing (3 Slice 1 + 4 Slice 2). Nenhuma regressão introduzida.

> **Pendente:** revisão visual humana contra a identidade RUÍDO (critério de aceite "Revisão de design humana aprova").
