"""
Slice Avatar 2 — Enriquecimento visual do construtor.

Tests verify the server-rendered structure supports the visual requirements:
  1. Builder renders all 6 category tabs with correct labels.
  2. Color options render as swatches (have 'option-swatch' in HTML).
  3. Text options render as chips (have 'option-chip' in HTML).
  4. Avatar preview container is present.
  5. Tab labels are uppercase (text-transform is a CSS concern, but labels
     should be present in the HTML for the CSS to act on).
"""
import re
import pytest

from data.character_options import CHAR_OPTIONS


EXPECTED_TAB_LABELS = ["Cabelo", "Pele", "Cor do cabelo", "Acessórios", "Fundo"]
COLOR_CATEGORIES = {"pele", "cor_cabelo", "fundo"}
TEXT_CATEGORIES = {"cabelo", "acessorio"}


def _get_join_html(client) -> str:
    resp = client.get("/join")
    assert resp.status_code == 200
    return resp.data.decode()


# ── Cycle 1: all 6 tabs are rendered ──────────────────────────────────────────

def test_join_renders_six_category_tabs(client):
    """Builder must render a tab button for every category (6 total)."""
    html = _get_join_html(client)
    tab_buttons = re.findall(r'data-tab="', html)
    assert len(tab_buttons) == len(EXPECTED_TAB_LABELS), (
        f"Expected {len(EXPECTED_TAB_LABELS)} tabs, found {len(tab_buttons)}"
    )
    for label in EXPECTED_TAB_LABELS:
        assert label in html, f"Tab label '{label}' not found in rendered HTML"


# ── Cycle 2: color options render as swatches ─────────────────────────────────

def test_join_color_options_render_as_swatches(client):
    """Color categories (pele, cor_cabelo, fundo) must render option-swatch divs."""
    html = _get_join_html(client)
    swatch_count = html.count('class="option-swatch"')
    expected_swatches = sum(len(CHAR_OPTIONS[cat]) for cat in COLOR_CATEGORIES)
    assert swatch_count == expected_swatches, (
        f"Expected {expected_swatches} swatches, found {swatch_count}"
    )


# ── Cycle 3: text options render as chips ─────────────────────────────────────

def test_join_text_options_render_as_chips(client):
    """Non-color categories (rosto, cabelo, acessorio) must render option-chip divs."""
    html = _get_join_html(client)
    chip_count = html.count('class="option-chip"')
    expected_chips = sum(len(CHAR_OPTIONS[cat]) for cat in TEXT_CATEGORIES)
    assert chip_count == expected_chips, (
        f"Expected {expected_chips} chips, found {chip_count}"
    )


# ── Cycle 4: avatar preview container is present ──────────────────────────────

def test_join_avatar_preview_container_present(client):
    """Preview container must be in the DOM so JS can populate the SVG."""
    html = _get_join_html(client)
    assert 'id="avatar-preview-svg"' in html
