"""
Issue 06 — Tela FINAL na TV: split de template + posters de consenso.

Testes via GET /desktop com manifesto injetado por monkeypatch.
"""
import json
import pytest
from extensions import db
from models import Session, Player, Vote


FAKE_MANIFEST = {
    "acao__die_hard": {"file": "static/img/posters/acao__die_hard.jpg"},
    "acao__mad_max":  {"file": "static/img/posters/acao__mad_max.jpg"},
}


def _add_player(session_id, name):
    p = Player(
        name=name,
        character_json=json.dumps({}),
        avatar_path="/static/img/avatars/test.png",
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


def _set_final(session, result_round=1):
    session.state = "FINAL"
    session.result_round = result_round
    db.session.flush()


# ── Cycle 1: FINAL renderiza container distinto ───────────────────────────────

def test_desktop_final_renders_distinct_layout(app, monkeypatch):
    import routes.game as gm
    monkeypatch.setattr(gm, "_manifest", {})

    with app.app_context():
        s = Session.query.first()
        _set_final(s, result_round=1)
        p1 = _add_player(s.id, "Alice")
        p2 = _add_player(s.id, "Bob")
        _add_vote(p1.id, 1, "acao__die_hard", "Die Hard")
        _add_vote(p2.id, 1, "acao__die_hard", "Die Hard")
        db.session.commit()

    resp = app.test_client().get("/desktop")
    html = resp.data.decode()

    assert resp.status_code == 200
    assert "desktop-final" in html
    assert "results-movies-grid" not in html


# ── Cycle 2: 1 consenso → hero ────────────────────────────────────────────────

def test_desktop_final_single_consensus_is_hero(app, monkeypatch):
    import routes.game as gm
    monkeypatch.setattr(gm, "_manifest", {})

    with app.app_context():
        s = Session.query.first()
        _set_final(s, result_round=1)
        p1 = _add_player(s.id, "Alice")
        p2 = _add_player(s.id, "Bob")
        _add_vote(p1.id, 1, "acao__die_hard", "Die Hard")
        _add_vote(p2.id, 1, "acao__die_hard", "Die Hard")
        db.session.commit()

    html = app.test_client().get("/desktop").data.decode()

    assert "final-hero" in html
    assert "final-posters-row" not in html
    assert "Die Hard" in html


# ── Cycle 3: 2+ consensos → fileira de posters ───────────────────────────────

def test_desktop_final_multiple_consensus_is_row(app, monkeypatch):
    import routes.game as gm
    monkeypatch.setattr(gm, "_manifest", {})

    with app.app_context():
        s = Session.query.first()
        _set_final(s, result_round=1)
        p1 = _add_player(s.id, "Alice")
        p2 = _add_player(s.id, "Bob")
        _add_vote(p1.id, 1, "acao__die_hard", "Die Hard")
        _add_vote(p2.id, 1, "acao__die_hard", "Die Hard")
        _add_vote(p1.id, 1, "acao__mad_max", "Mad Max")
        _add_vote(p2.id, 1, "acao__mad_max", "Mad Max")
        db.session.commit()

    html = app.test_client().get("/desktop").data.decode()

    assert "final-posters-row" in html
    assert "final-hero" not in html
    assert "Die Hard" in html
    assert "Mad Max" in html


# ── Cycle 4: filmes sem match NÃO aparecem na área de destaque ────────────────

def test_desktop_final_nonmatch_not_featured(app, monkeypatch):
    import routes.game as gm
    monkeypatch.setattr(gm, "_manifest", {})

    with app.app_context():
        s = Session.query.first()
        _set_final(s, result_round=1)
        p1 = _add_player(s.id, "Alice")
        p2 = _add_player(s.id, "Bob")
        # match
        _add_vote(p1.id, 1, "acao__die_hard", "Die Hard")
        _add_vote(p2.id, 1, "acao__die_hard", "Die Hard")
        # non-match (só P1)
        _add_vote(p1.id, 1, "acao__mad_max", "Mad Max")
        db.session.commit()

    html = app.test_client().get("/desktop").data.decode()

    assert "final-hero" in html
    assert "Die Hard" in html
    assert "Mad Max" not in html


# ── Cycle 5: poster real usado quando disponível ─────────────────────────────

def test_desktop_final_poster_used_when_in_manifest(app, monkeypatch):
    import routes.game as gm
    monkeypatch.setattr(gm, "_manifest", FAKE_MANIFEST)

    with app.app_context():
        s = Session.query.first()
        _set_final(s, result_round=1)
        p1 = _add_player(s.id, "Alice")
        p2 = _add_player(s.id, "Bob")
        _add_vote(p1.id, 1, "acao__die_hard", "Die Hard")
        _add_vote(p2.id, 1, "acao__die_hard", "Die Hard")
        db.session.commit()

    html = app.test_client().get("/desktop").data.decode()

    assert "static/img/posters/acao__die_hard.jpg" in html


# ── Cycle 6: sem poster → placeholder sem crash ───────────────────────────────

def test_desktop_final_no_poster_placeholder(app, monkeypatch):
    import routes.game as gm
    monkeypatch.setattr(gm, "_manifest", {})

    with app.app_context():
        s = Session.query.first()
        _set_final(s, result_round=1)
        p1 = _add_player(s.id, "Alice")
        p2 = _add_player(s.id, "Bob")
        _add_vote(p1.id, 1, "acao__die_hard", "Die Hard")
        _add_vote(p2.id, 1, "acao__die_hard", "Die Hard")
        db.session.commit()

    html = app.test_client().get("/desktop").data.decode()

    assert "final-hero" in html
    assert "final-hero-poster" in html
    # placeholder initial present (no poster injected)
    assert "final-hero-initial" in html
    assert "Die Hard" in html


# ── Cycle 7: SHOW_1 continua renderizando a grade (regressão) ────────────────

def test_desktop_show1_renders_movies_grid(app, monkeypatch):
    import routes.game as gm
    monkeypatch.setattr(gm, "_manifest", {})

    with app.app_context():
        s = Session.query.first()
        s.state = "SHOW_1"
        db.session.flush()
        p1 = _add_player(s.id, "Alice")
        p2 = _add_player(s.id, "Bob")
        _add_vote(p1.id, 1, "acao__die_hard", "Die Hard")
        _add_vote(p2.id, 1, "acao__mad_max", "Mad Max")
        db.session.commit()

    html = app.test_client().get("/desktop").data.decode()

    assert "results-movies-grid" in html
    assert "desktop-final" not in html


# ── Cycle 8: botão ENCERRAR presente no FINAL ─────────────────────────────────

def test_desktop_final_has_encerrar_button(app, monkeypatch):
    import routes.game as gm
    monkeypatch.setattr(gm, "_manifest", {})

    with app.app_context():
        s = Session.query.first()
        _set_final(s, result_round=1)
        p1 = _add_player(s.id, "Alice")
        p2 = _add_player(s.id, "Bob")
        _add_vote(p1.id, 1, "acao__die_hard", "Die Hard")
        _add_vote(p2.id, 1, "acao__die_hard", "Die Hard")
        db.session.commit()

    html = app.test_client().get("/desktop").data.decode()

    assert "ENCERRAR" in html
    assert "endSession()" in html
