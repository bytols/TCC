"""
Slice Avatar 1 — Bugfix: avatar builder state preservation.

Tests verify server-rendered HTML behaviour through the public HTTP interface.
JS-only behaviour (tab switching, live preview updates) is covered by the
acceptance criteria and tested manually; here we test what the server controls:
  1. Initial checked state reflects CHAR_DEFAULTS, not always loop.first.
  2. Error re-render restores the character values the user had submitted.
  3. Submitted (non-default) character values are persisted in character_json.
"""
import json
import re

import pytest

from data.character_options import CHAR_DEFAULTS


# ── helpers ───────────────────────────────────────────────────────────────────

def _checked_radios(html: str) -> dict[str, str]:
    """Return {name: value} for every radio input that carries `checked`."""
    result: dict[str, str] = {}
    for tag in re.findall(r"<input[^>]+>", html, re.DOTALL):
        if 'type="radio"' not in tag:
            continue
        if "checked" not in tag:
            continue
        name_m = re.search(r'name="([^"]+)"', tag)
        val_m = re.search(r'value="([^"]+)"', tag)
        if name_m and val_m:
            result[name_m.group(1)] = val_m.group(1)
    return result


# ── Cycle 1: initial checked state ────────────────────────────────────────────

def test_get_join_checks_char_defaults(client):
    """GET /join must pre-check CHAR_DEFAULTS values, not always loop.first."""
    resp = client.get("/join")
    assert resp.status_code == 200

    checked = _checked_radios(resp.data.decode())

    for category, default_id in CHAR_DEFAULTS.items():
        assert checked.get(category) == default_id, (
            f"Category '{category}': expected checked='{default_id}', "
            f"got checked='{checked.get(category)}'"
        )


# ── Cycle 2: error re-render preserves submitted character ────────────────────

def test_post_join_duplicate_name_preserves_character(client, add_player):
    """POST /join with duplicate name re-renders with the submitted character."""
    add_player(name="Alice")

    non_default = {
        "cabelo": "moicano",
        "pele": "pele_7",
        "cor_cabelo": "cab_6",
        "acessorio": "oculos",
        "fundo": "fundo_verde",
    }
    resp = client.post("/join", data={"name": "Alice", **non_default})
    assert resp.status_code == 400

    checked = _checked_radios(resp.data.decode())

    for category, submitted_id in non_default.items():
        assert checked.get(category) == submitted_id, (
            f"Category '{category}': expected '{submitted_id}' after error, "
            f"got '{checked.get(category)}'"
        )


# ── Cycle 3: non-default choices are saved in character_json ──────────────────

def test_post_join_saves_submitted_character(client):
    """POST /join with non-default character values persists them in DB."""
    from models import Player

    resp = client.post("/join", data={
        "name": "Bob",
        "cabelo": "coque",
        "pele": "pele_5",
        "cor_cabelo": "cab_4",
        "acessorio": "chapeu",
        "fundo": "fundo_grafite",
    }, follow_redirects=False)

    assert resp.status_code == 302

    player = Player.query.filter_by(name="Bob").first()
    assert player is not None
    char = json.loads(player.character_json)
    assert char["cabelo"] == "coque"
    assert char["pele"] == "pele_5"
    assert char["acessorio"] == "chapeu"
