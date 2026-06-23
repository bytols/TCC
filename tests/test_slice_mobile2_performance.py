"""
Slice Mobile 2 — Performance: app fluido e responsivo no mobile.

Causa raiz do travamento: .glow-layer::before/::after anima filter:blur(95-105px)
em tela cheia infinitamente; ~12 tiles de gênero empilham backdrop-filter sobre
essa superfície borrada em movimento; o deck monta um DOM node por filme do catálogo.

Estes testes verificam as três correções:
  1. blob-drift desabilitado em touch (@media pointer:coarse → animation:none)
  2. raio de blur dos blobs reduzido no mobile (≤ 40 px)
  3. --glass-blur reduzido no mobile (≤ 6 px)
  4. backdrop-filter removido de .genre-tile no mobile (grid scrollável)
  5. DECK_WINDOW definido em round.js
  6. buildDeck não usa items.map para montar DOM (padrão que cria N nodes)
"""
import re
import pathlib

CSS_PATH = pathlib.Path(__file__).parent.parent / "static" / "css" / "main.css"
JS_PATH  = pathlib.Path(__file__).parent.parent / "static" / "js" / "round.js"


def _css() -> str:
    return CSS_PATH.read_text()


def _js() -> str:
    return JS_PATH.read_text()


def _coarse_block(css: str) -> str:
    """Extrai o conteúdo do bloco @media (pointer: coarse) lidando com chaves aninhadas."""
    m = re.search(r'@media\s*\(\s*pointer\s*:\s*coarse\s*\)', css)
    assert m, "@media (pointer: coarse) não encontrado em main.css"
    start = css.index('{', m.end())
    depth, i = 0, start
    while i < len(css):
        if css[i] == '{':
            depth += 1
        elif css[i] == '}':
            depth -= 1
            if depth == 0:
                return css[start + 1:i]
        i += 1
    raise AssertionError("@media (pointer: coarse) não está fechado corretamente")


# ── Cycle 1: animation: none nos blobs ao toque ──────────────────────────────

def test_mobile_glow_animation_disabled():
    """
    blob-drift anima filter:blur(95-105px) em tela cheia → GPU redraw por frame.
    @media (pointer: coarse) deve zerar a animação dos pseudoelementos do glow.
    """
    block = _coarse_block(_css())
    assert re.search(r'animation\s*:\s*none', block), \
        "@media (pointer: coarse) deve conter 'animation: none' para parar blob-drift"


# ── Cycle 2: raio de blur reduzido no mobile ─────────────────────────────────

def test_mobile_glow_blur_radius_reduced():
    """
    95-105 px de blur exige amostragem de muitos pixels vizinhos por pixel.
    No mobile o raio deve ser ≤ 40 px.
    """
    block = _coarse_block(_css())
    radii = re.findall(r'filter\s*:\s*blur\((\d+)px\)', block)
    assert radii, "@media (pointer: coarse) deve redefinir filter:blur() nos blobs de glow"
    for r in radii:
        assert int(r) <= 40, \
            f"Raio de blur no bloco mobile deve ser ≤ 40 px, encontrado {r} px"


# ── Cycle 3: --glass-blur reduzido no mobile ─────────────────────────────────

def test_mobile_glass_blur_token_reduced():
    """
    --glass-blur conduz backdrop-filter em ~10 elementos por tela.
    No mobile deve ser ≤ blur(6px) para reduzir custo de compositing.
    """
    block = _coarse_block(_css())
    m = re.search(r'--glass-blur\s*:\s*blur\((\d+)px\)', block)
    assert m, "@media (pointer: coarse) deve sobrescrever --glass-blur"
    assert int(m.group(1)) <= 6, \
        f"--glass-blur no mobile deve ser ≤ 6 px, encontrado {m.group(1)} px"


# ── Cycle 4: backdrop-filter removido do grid scrollável ─────────────────────

def test_mobile_genre_tile_no_backdrop_filter():
    """
    .genre-tile renderiza em grid scrollável com backdrop-filter:blur(10px).
    Scroll sobre backdrop borrado dispara repaint por frame no mobile.
    O bloco mobile deve remover o backdrop-filter desses tiles.
    """
    block = _coarse_block(_css())
    assert '.genre-tile' in block, \
        "@media (pointer: coarse) deve conter regra para .genre-tile"
    rule_m = re.search(r'\.genre-tile\s*\{([^}]+)\}', block)
    assert rule_m, "Regra .genre-tile não encontrada em @media (pointer: coarse)"
    rule = rule_m.group(1)
    assert re.search(r'backdrop-filter\s*:\s*none', rule), \
        ".genre-tile no bloco mobile deve definir backdrop-filter: none"


# ── Cycle 5: DECK_WINDOW definido ────────────────────────────────────────────

def test_deck_window_constant_defined():
    """
    round.js deve definir DECK_WINDOW para limitar o número de nós DOM criados
    no deck. Sem esse limite, o deck monta um elemento por filme (~20-50),
    custoso no render inicial no mobile.
    """
    assert 'DECK_WINDOW' in _js(), \
        "round.js deve definir a constante DECK_WINDOW"


# ── Cycle 6: buildDeck não usa items.map ─────────────────────────────────────

def test_deck_does_not_create_all_items_as_dom():
    """
    O padrão 'cards = items.map(...)' cria um nó DOM por item do catálogo.
    buildDeck deve criar apenas os cards da janela visível (DECK_WINDOW), não N.
    """
    assert 'cards = items.map' not in _js(), \
        "buildDeck não deve usar items.map() para criar DOM — use janela limitada (DECK_WINDOW)"
