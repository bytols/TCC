"""
Slice 3 — Frontend reads local poster from payload; /api/poster removed.
Slice 2 (catalog serving with poster field) tested here as the required blocker.

Manifest is injected via monkeypatch so tests run without data/posters.json.
"""
import json
import re
import pytest
from unittest.mock import patch
from app import create_app
from extensions import db as _db
import session_state
from models import Player, Session, RoundPool


@pytest.fixture()
def app():
    application = create_app({"TESTING": True})
    with application.app_context():
        _db.drop_all()
        _db.create_all()
        session_state.get_or_create_session()
        yield application
        _db.session.remove()
        _db.drop_all()


def _add_player(app, name="P1"):
    with app.app_context():
        sess = Session.query.first()
        p = Player(
            name=name,
            character_json=json.dumps({}),
            avatar_path="/static/img/avatars/test.png",
            session_id=sess.id,
        )
        _db.session.add(p)
        _db.session.commit()
        return p.id


def _set_state(app, state):
    with app.app_context():
        sess = Session.query.first()
        sess.state = state
        _db.session.commit()


def _client_for_player(app, player_id):
    c = app.test_client()
    c.set_cookie("player_id", str(player_id))
    return c


def _parse_movies_data(html: str) -> dict:
    m = re.search(
        r'<script id="movies-data"[^>]*>(.*?)</script>', html, re.DOTALL
    )
    assert m, "movies-data script tag not found in response"
    return json.loads(m.group(1))


FAKE_MANIFEST = {
    "acao__die_hard": {"tmdb_id": 862, "file": "static/img/posters/acao__die_hard.jpg"},
}


# ── Cycle 1: /api/poster route removed ────────────────────────────────────────

def test_api_poster_route_removed(app):
    client = app.test_client()
    resp = client.get("/api/poster/acao__die_hard")
    assert resp.status_code == 404


# ── Cycle 2: payload has poster field + orphans excluded ──────────────────────

def test_round1_verified_movie_has_poster_in_payload(app, monkeypatch):
    import routes.game as gm
    monkeypatch.setattr(gm, "_manifest", FAKE_MANIFEST)

    pid = _add_player(app)
    _set_state(app, "ROUND_1")
    client = _client_for_player(app, pid)

    resp = client.get("/round/1")
    assert resp.status_code == 200

    data = _parse_movies_data(resp.data.decode())
    all_movies = [m for cat in data.values() for m in cat["movies"]]

    die_hard = next((m for m in all_movies if m["id"] == "acao__die_hard"), None)
    assert die_hard is not None, "acao__die_hard should appear in payload"
    assert die_hard["poster"] == "static/img/posters/acao__die_hard.jpg"


def test_round1_orphan_excluded_from_payload(app, monkeypatch):
    import routes.game as gm
    monkeypatch.setattr(gm, "_manifest", FAKE_MANIFEST)

    pid = _add_player(app)
    _set_state(app, "ROUND_1")
    client = _client_for_player(app, pid)

    resp = client.get("/round/1")
    assert resp.status_code == 200

    data = _parse_movies_data(resp.data.decode())
    all_ids = [m["id"] for cat in data.values() for m in cat["movies"]]

    assert "acao__mad_max" not in all_ids, "orphan must be excluded"
    assert "acao__die_hard" in all_ids, "verified movie must be included"


def test_round1_every_served_movie_has_poster(app, monkeypatch):
    import routes.game as gm
    manifest = {
        "acao__die_hard": {"tmdb_id": 862, "file": "static/img/posters/acao__die_hard.jpg"},
        "anim__spirited_away": {"tmdb_id": 129, "file": "static/img/posters/anim__spirited_away.jpg"},
    }
    monkeypatch.setattr(gm, "_manifest", manifest)

    pid = _add_player(app)
    _set_state(app, "ROUND_1")
    client = _client_for_player(app, pid)

    resp = client.get("/round/1")
    assert resp.status_code == 200

    data = _parse_movies_data(resp.data.decode())
    all_movies = [m for cat in data.values() for m in cat["movies"]]
    assert len(all_movies) == 2
    for m in all_movies:
        assert "poster" in m, f"movie {m['id']} missing poster field"


# ── Cycle 3: pool_grouped carries poster ─────────────────────────────────────

def _seed_pool(app, round_number, entries):
    """entries: list of (movie_id, category)"""
    with app.app_context():
        for movie_id, category in entries:
            _db.session.add(RoundPool(
                round_number=round_number,
                movie_id=movie_id,
                movie_title=movie_id,
                category=category,
            ))
        _db.session.commit()


def test_pool_grouped_carries_poster(app, monkeypatch):
    import routes.game as gm
    monkeypatch.setattr(gm, "_manifest", FAKE_MANIFEST)

    _seed_pool(app, 2, [("acao__die_hard", "acao")])

    with app.app_context():
        result = gm.pool_grouped(2)

    movies = result["acao"]["movies"]
    assert len(movies) == 1
    assert movies[0]["poster"] == "static/img/posters/acao__die_hard.jpg"


def test_pool_grouped_orphan_has_no_poster(app, monkeypatch):
    import routes.game as gm
    monkeypatch.setattr(gm, "_manifest", {})  # nothing in manifest

    _seed_pool(app, 2, [("acao__die_hard", "acao")])

    with app.app_context():
        result = gm.pool_grouped(2)

    movies = result["acao"]["movies"]
    assert len(movies) == 1
    assert "poster" not in movies[0]
