"""
Slice TV 1 — Posters nas telas SHOW_1 / SHOW_2.

GET /desktop com manifesto injetado por monkeypatch confirma:
- poster real quando presente (has-poster + background-image)
- placeholder (gradiente + inicial) quando ausente
"""
import json
import pytest
from extensions import db
from models import Session, Player, Vote


FAKE_MANIFEST = {
    "acao__die_hard": {"file": "static/img/posters/acao__die_hard.jpg"},
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


# ── Cycle 1: SHOW_1 usa poster real quando disponível ────────────────────────

def test_show1_poster_used_when_in_manifest(app, monkeypatch):
    import routes.game as gm
    monkeypatch.setattr(gm, "_manifest", FAKE_MANIFEST)

    with app.app_context():
        s = Session.query.first()
        s.state = "SHOW_1"
        db.session.flush()
        p1 = _add_player(s.id, "Alice")
        p2 = _add_player(s.id, "Bob")
        _add_vote(p1.id, 1, "acao__die_hard", "Die Hard")
        _add_vote(p2.id, 1, "acao__die_hard", "Die Hard")
        db.session.commit()

    resp = app.test_client().get("/desktop")
    html = resp.data.decode()

    assert resp.status_code == 200
    assert "static/img/posters/acao__die_hard.jpg" in html
    assert "has-poster" in html


# ── Cycle 2: SHOW_1 sem poster → placeholder sem crash ───────────────────────

def test_show1_no_poster_shows_placeholder(app, monkeypatch):
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

    resp = app.test_client().get("/desktop")
    html = resp.data.decode()

    assert resp.status_code == 200
    assert "results-movies-grid" in html
    assert "result-movie-initial" in html
    assert "static/img/posters/" not in html


# ── Cycle 3: SHOW_2 usa poster real quando disponível ────────────────────────

def test_show2_poster_used_when_in_manifest(app, monkeypatch):
    import routes.game as gm
    monkeypatch.setattr(gm, "_manifest", FAKE_MANIFEST)

    with app.app_context():
        s = Session.query.first()
        s.state = "SHOW_2"
        db.session.flush()
        p1 = _add_player(s.id, "Alice")
        p2 = _add_player(s.id, "Bob")
        _add_vote(p1.id, 2, "acao__die_hard", "Die Hard")
        _add_vote(p2.id, 2, "acao__die_hard", "Die Hard")
        db.session.commit()

    resp = app.test_client().get("/desktop")
    html = resp.data.decode()

    assert resp.status_code == 200
    assert "static/img/posters/acao__die_hard.jpg" in html
    assert "has-poster" in html


# ── Cycle 4: SHOW_2 sem poster → placeholder sem crash ───────────────────────

def test_show2_no_poster_shows_placeholder(app, monkeypatch):
    import routes.game as gm
    monkeypatch.setattr(gm, "_manifest", {})

    with app.app_context():
        s = Session.query.first()
        s.state = "SHOW_2"
        db.session.flush()
        p1 = _add_player(s.id, "Alice")
        p2 = _add_player(s.id, "Bob")
        _add_vote(p1.id, 2, "acao__die_hard", "Die Hard")
        _add_vote(p2.id, 2, "acao__mad_max", "Mad Max")
        db.session.commit()

    resp = app.test_client().get("/desktop")
    html = resp.data.decode()

    assert resp.status_code == 200
    assert "results-movies-grid" in html
    assert "result-movie-initial" in html
    assert "static/img/posters/" not in html


# ── Cycle 5: CSS garante background-size cover para has-poster ───────────────

def test_css_has_poster_background_size_cover():
    with open("static/css/main.css", encoding="utf-8") as f:
        css = f.read()

    assert "result-movie-poster.has-poster" in css
    assert "background-size: cover" in css
