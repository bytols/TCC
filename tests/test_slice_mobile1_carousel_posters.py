"""
Slice Mobile 1 — Posters visíveis no carrossel.

O colapso de layout deixava o deck-card com altura zero no mobile porque
aspect-ratio em elementos absolutamente posicionados pode falhar no Safari iOS
quando o container pai tem min-height: 0 (padrão flex).

Estes testes verificam que o CSS garante:
  1. altura mínima concreta no palco do deck (.deck), não apenas 0
  2. fallback de altura no card (.deck-card) independente de aspect-ratio
"""
import re
import pathlib

CSS_PATH = pathlib.Path(__file__).parent.parent / "static" / "css" / "main.css"


def _read_css():
    return CSS_PATH.read_text()


def _extract_rule(css: str, selector: str) -> str:
    pattern = re.escape(selector) + r"\s*\{([^}]+)\}"
    m = re.search(pattern, css)
    assert m, f"Selector '{selector}' not found in CSS"
    return m.group(1)


def _parse_min_height_px(rule: str) -> int | None:
    m = re.search(r"min-height:\s*(\d+)px", rule)
    return int(m.group(1)) if m else None


# ── Cycle 1: .deck must have a concrete min-height floor ─────────────────────

def test_deck_stage_has_concrete_min_height():
    """
    .deck needs a px min-height so the absolutely-positioned cards have a
    real stage — prevents zero-height on mobile when aspect-ratio is ignored.
    """
    css = _read_css()
    rule = _extract_rule(css, ".deck")
    min_h = _parse_min_height_px(rule)
    assert min_h is not None, ".deck must have an explicit min-height in px (not just 0 or absent)"
    assert min_h >= 200, f".deck min-height must be ≥ 200px to keep posters visible (got {min_h}px)"


# ── Cycle 2: .deck-card must have a min-height fallback ──────────────────────

def test_deck_card_has_min_height_fallback():
    """
    .deck-card relies on aspect-ratio: 2/3 for height, which can fail on
    mobile Safari. An explicit min-height ensures the poster area is never zero.
    """
    css = _read_css()
    rule = _extract_rule(css, ".deck-card")
    min_h = _parse_min_height_px(rule)
    assert min_h is not None, ".deck-card must have an explicit min-height as aspect-ratio fallback"
    assert min_h >= 150, f".deck-card min-height must be ≥ 150px (got {min_h}px)"
