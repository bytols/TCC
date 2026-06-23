"""
Issue 07 — Tela FINAL na TV: cartão de tempo + avatares dos participantes.

Testes via GET /desktop com manifesto injetado por monkeypatch.
"""
import json
import pytest
from extensions import db
from models import Session, Player, Vote


def _add_player(session_id, name, avatar="/static/img/avatars/test.png"):
    p = Player(
        name=name,
        character_json=json.dumps({}),
        avatar_path=avatar,
        session_id=session_id,
    )
    db.session.add(p)
    db.session.flush()
    return p


def _add_vote(player_id, round_number, movie_id, movie_title="Movie", category="acao"):
    db.session.add(Vote(
        player_id=player_id,
        round_number=round_number,
        movie_id=movie_id,
        movie_title=movie_title,
        category=category,
    ))
    db.session.flush()


def _set_final(session, result_round=1, result_seconds=None):
    session.state = "FINAL"
    session.result_round = result_round
    session.result_seconds = result_seconds
    db.session.flush()


# ── Cycle 1: FINAL renderiza cartão de tempo ─────────────────────────────────

def test_desktop_final_has_time_card(app, monkeypatch):
    import routes.game as gm
    monkeypatch.setattr(gm, "_manifest", {})

    with app.app_context():
        s = Session.query.first()
        _set_final(s, result_round=1, result_seconds=125)
        p1 = _add_player(s.id, "Alice")
        p2 = _add_player(s.id, "Bob")
        _add_vote(p1.id, 1, "acao__die_hard", "Die Hard")
        _add_vote(p2.id, 1, "acao__die_hard", "Die Hard")
        db.session.commit()

    html = app.test_client().get("/desktop").data.decode()

    assert "final-time-card" in html


# ── Cycle 2: Rótulo TEMPO presente ───────────────────────────────────────────

def test_desktop_final_time_card_has_tempo_label(app, monkeypatch):
    import routes.game as gm
    monkeypatch.setattr(gm, "_manifest", {})

    with app.app_context():
        s = Session.query.first()
        _set_final(s, result_round=1, result_seconds=125)
        p1 = _add_player(s.id, "Alice")
        p2 = _add_player(s.id, "Bob")
        _add_vote(p1.id, 1, "acao__die_hard", "Die Hard")
        _add_vote(p2.id, 1, "acao__die_hard", "Die Hard")
        db.session.commit()

    html = app.test_client().get("/desktop").data.decode()

    assert "TEMPO" in html


# ── Cycle 3: Tempo formatado como MM:SS ──────────────────────────────────────

def test_desktop_final_time_formatted_mmss(app, monkeypatch):
    import routes.game as gm
    monkeypatch.setattr(gm, "_manifest", {})

    with app.app_context():
        s = Session.query.first()
        _set_final(s, result_round=1, result_seconds=125)  # 02:05
        p1 = _add_player(s.id, "Alice")
        p2 = _add_player(s.id, "Bob")
        _add_vote(p1.id, 1, "acao__die_hard", "Die Hard")
        _add_vote(p2.id, 1, "acao__die_hard", "Die Hard")
        db.session.commit()

    html = app.test_client().get("/desktop").data.decode()

    assert "02:05" in html


# ── Cycle 4: result_seconds None → sem crash, cartão omitido ─────────────────

def test_desktop_final_no_result_seconds_no_crash(app, monkeypatch):
    import routes.game as gm
    monkeypatch.setattr(gm, "_manifest", {})

    with app.app_context():
        s = Session.query.first()
        _set_final(s, result_round=1, result_seconds=None)
        p1 = _add_player(s.id, "Alice")
        p2 = _add_player(s.id, "Bob")
        _add_vote(p1.id, 1, "acao__die_hard", "Die Hard")
        _add_vote(p2.id, 1, "acao__die_hard", "Die Hard")
        db.session.commit()

    resp = app.test_client().get("/desktop")
    html = resp.data.decode()

    assert resp.status_code == 200
    assert "desktop-final" in html
    assert "final-time-card" not in html


# ── Cycle 5: Linha de avatares renderizada ───────────────────────────────────

def test_desktop_final_has_avatars_row(app, monkeypatch):
    import routes.game as gm
    monkeypatch.setattr(gm, "_manifest", {})

    with app.app_context():
        s = Session.query.first()
        _set_final(s, result_round=1, result_seconds=60)
        p1 = _add_player(s.id, "Alice")
        p2 = _add_player(s.id, "Bob")
        _add_vote(p1.id, 1, "acao__die_hard", "Die Hard")
        _add_vote(p2.id, 1, "acao__die_hard", "Die Hard")
        db.session.commit()

    html = app.test_client().get("/desktop").data.decode()

    assert "final-avatars-row" in html


# ── Cycle 6: Um avatar por participante ──────────────────────────────────────

def test_desktop_final_one_avatar_per_player(app, monkeypatch):
    import routes.game as gm
    monkeypatch.setattr(gm, "_manifest", {})

    with app.app_context():
        s = Session.query.first()
        _set_final(s, result_round=1, result_seconds=60)
        p1 = _add_player(s.id, "Alice")
        p2 = _add_player(s.id, "Bob")
        _add_vote(p1.id, 1, "acao__die_hard", "Die Hard")
        _add_vote(p2.id, 1, "acao__die_hard", "Die Hard")
        db.session.commit()

    html = app.test_client().get("/desktop").data.decode()

    assert html.count("final-avatar-item") == 2
