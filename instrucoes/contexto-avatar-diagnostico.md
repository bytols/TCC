# Diagnóstico: Avatar Builder — estado atual e próximos passos

> Criado em: 2026-06-23
> Para: retomada em chat com contexto limpo

---

## O que foi investigado

Investigação completa do construtor de avatar após o usuário relatar "Os avatares continuam bugada". A análise incluiu: leitura do código (avatar.py, avatar.js, join.html, main.css, character_options.py, join.py), renderização de PNGs via cairosvg, screenshots do browser via Playwright (Node.js direto, sem MCP), e verificação do estado DOM em runtime.

---

## Resultado do diagnóstico

### Bugs funcionais: RESOLVIDOS

Os bugs descritos em `instrucoes/issues/done/slice-avatar-1-bugfix.md` estão **corrigidos e verificados**:

- **Estado entre abas**: ao trocar de aba e voltar, o radio button permanece marcado. Verificado via `page.evaluate()` — `checked: true` e `labelSelected: true` persistem após troca de aba.
- **Preview ao vivo**: `updateAvatar()` é chamado via `onchange` em cada radio. A função `window.buildAvatarSVG(character)` gera o SVG corretamente e injeta no `#avatar-preview-svg`.
- **Defaults corretos**: `join.py` GET passa `char_defaults=CHAR_DEFAULTS`; template usa `{% if opt.id == char_defaults[key] %}` para marcar o item correto ao carregar a página.
- **Zero erros de JS no console** na página de join.

### Visual do SVG gerado: COMPATÍVEL COM AS REFERÊNCIAS

Imagens de referência do usuário (`Desktop/personagens/1.JPG`, `2.JPG`, `3.JPG`) mostram:
- 1.JPG e 2.JPG: personagem com **coque** (coque style), pele escura (~pele_6 `#8D5524`), fundo roxo
- 3.JPG: personagem com **cacheado** (curly), pele escura, fundo roxo

Os SVGs gerados por `avatar.py` para essas combinações produzem resultado **visualmente equivalente às referências** (confirmado renderizando PNGs via cairosvg e comparando).

### Problema visual identificado: AVATAR DEFAULT parece "careca"

O avatar padrão (`liso_curto` + `pele_2` #F1C27D) é o que aparece ao abrir o form pela primeira vez. Visualmente:
- O cabelo "liso curto" é apenas um arco fino preto (`cap` path: M56,82 C56,42 144,42 144,82…)
- Com pele clara, o arco fino quase desaparece visualmente — parece uma faixa/headband, não cabelo
- O personagem parece quase careca na primeira impressão

Isso pode ser o que o usuário chama de "bugado" — o estado default do builder é visualmente pobre, não convida à personalização.

---

## Screenshots tiradas (via Node.js + Playwright)

```
/tmp/join_page.png        — splash screen (ok)
/tmp/join_form.png        — form aberto, avatar default (liso_curto claro)
/tmp/tab_cabelo.png       — aba CABELO aberta, liso_curto selecionado
/tmp/coque.png            — coque selecionado, preview atualizado corretamente
```

O browser funciona via:
```js
const { chromium } = require('/home/erick_leo/.npm/_npx/e41f203b7505f1fb/node_modules/playwright-core');
chromium.launch({
  executablePath: '/home/erick_leo/.cache/ms-playwright/chromium-1228/chrome-linux64/chrome',
  args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
})
```
(O MCP do Playwright não funciona — está configurado para "chrome" que não existe. Usar Node.js direto.)

---

## O que ainda não foi investigado

- Como os avatares aparecem na **TV/lobby desktop** (`/desktop`) — como `<img>` de 60px e 26px
- Como os avatares aparecem na **tela final** (`final-avatar-img`)
- Se o `object-fit: cover` em `<img>` para SVG com dimensões fixas (200px) está correto visualmente
- Se há diferença entre o avatar visto no mobile (builder) e o avatar visto na TV (lobby)

---

## Hipóteses pendentes de verificação

1. **Default feio**: mudar o avatar default para `coque` + `pele_6` ou similar, que visualmente é mais apelativo e próximo das referências
2. **liso_curto path muito fino**: o arco do `liso_curto` ocupa pouco espaço vertical (apenas ~10px); aumentar a altura do cap pode melhorar a aparência
3. **Bug no lobby/TV**: avatares podem não carregar ou aparecer cortados na tela TV — não foi verificado
4. **SVG em `<img>` com `object-fit: cover`**: SVG tem dimensões fixas `width="200" height="200"` — pode não redimensionar bem em algumas combinações de browser

---

## Arquivos-chave

| Arquivo | Papel |
|---|---|
| `avatar.py` | Geração do SVG final (server-side) |
| `static/js/avatar.js` | Espelho JS para preview ao vivo |
| `data/character_options.py` | CHAR_OPTIONS + CHAR_DEFAULTS |
| `templates/mobile/join.html` | Form de criação de identidade |
| `static/css/main.css` | CSS do builder (`.char-preview-wrap`, `.option-swatch`, etc.) |
| `templates/desktop/lobby.html` | Exibição de avatares como chips (`player-avatar`, `chip-avatar`, `final-avatar-img`) |
| `static/img/avatars/` | SVGs gerados persistidos em disco |

---

## Próximos passos sugeridos

1. **Screenshot do lobby/TV com jogadores** para ver como os avatares aparecem como chips e na tela final
2. **Decidir**: o avatar default "liso_curto + pele_2" será mantido ou trocado por um padrão mais expressivo?
3. **Revisar visualmente** o liso_curto, liso_longo e moicano — são os estilos menos testados visualmente
4. **Aprovar ou iterar** sobre o design dos swatches/chips no builder conforme critério de aceite do Slice Avatar 2

---

## Como rodar para testar

```bash
cd ~/tcc_mary
source venv/bin/activate
python run.py  # porta 5001

# Desktop (TV): http://localhost:5001/desktop
# Mobile (join): http://localhost:5001/join
```

O QR code na tela desktop aponta para o IP real da rede Wi-Fi (WSL2 detecta via `ipconfig.exe`).
