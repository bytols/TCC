"""
Issue 05 — Tela final: spine de dados (poster + year no resultado + consensus_movies no FINAL).

Acceptance criteria:
- GET /desktop em FINAL entrega poster quando id está no manifesto, sem poster quando não está.
- GET /desktop em FINAL expõe consensus_movies com apenas is_match==True, ordem decrescente.
- GET /results (mobile) passa pelo mesmo enriquecimento: itens com id no manifesto carregam poster.
- O campo year é injetado a partir de MOVIE_LOOKUP quando disponível.
- O cálculo de match permanece puro: sem dependência de manifesto/IO no módulo match.

Manifesto injetado via monkeypatch — sem dependência de data/posters.json real.
"""
import json
import pytest
from contextlib import contextmanager
from flask import template_rendered
from extensions import db
from models import Session, Player, Vote


# ── helpers ───────────────────────────────────────────────────────────────────

FAKE_MANIFEST = {
    "acao__die_hard": {"tmdb_id": 862, "file": "static/img/posters/acao__die_hard.jpg"},
}


@contextmanager
def capture_context(app):
    """Capture Jinja2 template context after a render."""
    ctx: dict = {}

    def record(sender, template, context, **extra):
        ctx.update(context)

    template_rendered.connect(record, app)
    try:
        yield ctx
    finally:
        template_rendered.disconnect(record, app)


def _add_player(session_id, name="P"):
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


# ── Cycle 1: /desktop FINAL → poster presente quando id está no manifesto ─────

def test_desktop_final_match_movie_has_poster(app, monkeypatch):
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

    client = app.test_client()
    with capture_context(app) as ctx:
        resp = client.get("/desktop")

    assert resp.status_code == 200
    movies = ctx["match_data"]["movies"]
    die_hard = next(m for m in movies if m["movie_id"] == "acao__die_hard")
    assert die_hard["poster"] == "static/img/posters/acao__die_hard.jpg"


# ── Cycle 2: /desktop FINAL → sem poster quando id não está no manifesto ──────

def test_desktop_final_orphan_movie_has_no_poster(app, monkeypatch):
    import routes.game as gm
    monkeypatch.setattr(gm, "_manifest", FAKE_MANIFEST)

    with app.app_context():
        s = Session.query.first()
        _set_final(s, result_round=1)
        p1 = _add_player(s.id, "Alice")
        p2 = _add_player(s.id, "Bob")
        _add_vote(p1.id, 1, "acao__mad_max", "Mad Max")
        _add_vote(p2.id, 1, "acao__mad_max", "Mad Max")
        db.session.commit()

    client = app.test_client()
    with capture_context(app) as ctx:
        resp = client.get("/desktop")

    assert resp.status_code == 200
    movies = ctx["match_data"]["movies"]
    mad_max = next(m for m in movies if m["movie_id"] == "acao__mad_max")
    assert "poster" not in mad_max


# ── Cycle 3: consensus_movies contém apenas is_match==True ────────────────────

def test_desktop_final_consensus_movies_only_matches(app, monkeypatch):
    import routes.game as gm
    monkeypatch.setattr(gm, "_manifest", FAKE_MANIFEST)

    with app.app_context():
        s = Session.query.first()
        _set_final(s, result_round=1)
        p1 = _add_player(s.id, "Alice")
        p2 = _add_player(s.id, "Bob")
        # "acao__die_hard" voted by both → is_match=True
        _add_vote(p1.id, 1, "acao__die_hard", "Die Hard")
        _add_vote(p2.id, 1, "acao__die_hard", "Die Hard")
        # "acao__mad_max" voted only by P1 → is_match=False
        _add_vote(p1.id, 1, "acao__mad_max", "Mad Max")
        db.session.commit()

    client = app.test_client()
    with capture_context(app) as ctx:
        resp = client.get("/desktop")

    assert resp.status_code == 200
    assert "consensus_movies" in ctx
    consensus = ctx["consensus_movies"]
    assert len(consensus) == 1
    assert consensus[0]["movie_id"] == "acao__die_hard"
    assert consensus[0]["is_match"] is True


# ── Cycle 4: consensus_movies em ordem decrescente de votos ──────────────────

def test_desktop_final_consensus_movies_descending_order(app, monkeypatch):
    import routes.game as gm
    manifest = {
        "acao__die_hard": {"file": "static/img/posters/acao__die_hard.jpg"},
        "acao__mad_max":  {"file": "static/img/posters/acao__mad_max.jpg"},
    }
    monkeypatch.setattr(gm, "_manifest", manifest)

    with app.app_context():
        s = Session.query.first()
        _set_final(s, result_round=1)
        p1 = _add_player(s.id, "Alice")
        p2 = _add_player(s.id, "Bob")
        p3 = _add_player(s.id, "Carol")
        # Regra nova (unanimidade): consensus_movies só inclui filmes votados por
        # TODOS os 3 ativos. Mad Max e Die Hard escolhidos pelos 3 → ambos match
        # (count==3); empatados, mantêm a ordem de inserção (Mad Max primeiro).
        _add_vote(p1.id, 1, "acao__mad_max", "Mad Max")
        _add_vote(p2.id, 1, "acao__mad_max", "Mad Max")
        _add_vote(p3.id, 1, "acao__mad_max", "Mad Max")
        _add_vote(p1.id, 1, "acao__die_hard", "Die Hard")
        _add_vote(p2.id, 1, "acao__die_hard", "Die Hard")
        _add_vote(p3.id, 1, "acao__die_hard", "Die Hard")
        db.session.commit()

    client = app.test_client()
    with capture_context(app) as ctx:
        resp = client.get("/desktop")

    assert resp.status_code == 200
    consensus = ctx["consensus_movies"]
    assert len(consensus) == 2
    assert consensus[0]["movie_id"] == "acao__mad_max"
    assert consensus[1]["movie_id"] == "acao__die_hard"


# ── Cycle 5: /results (mobile) também enriquece com poster ───────────────────

def test_results_mobile_match_movie_has_poster(app, monkeypatch):
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
        p1_id = p1.id

    client = app.test_client()
    client.set_cookie("player_id", str(p1_id))
    with capture_context(app) as ctx:
        resp = client.get("/results")

    assert resp.status_code == 200
    movies = ctx["match_data"]["movies"]
    die_hard = next(m for m in movies if m["movie_id"] == "acao__die_hard")
    assert die_hard["poster"] == "static/img/posters/acao__die_hard.jpg"


def test_results_mobile_orphan_has_no_poster(app, monkeypatch):
    import routes.game as gm
    monkeypatch.setattr(gm, "_manifest", FAKE_MANIFEST)

    with app.app_context():
        s = Session.query.first()
        _set_final(s, result_round=1)
        p1 = _add_player(s.id, "Alice")
        p2 = _add_player(s.id, "Bob")
        _add_vote(p1.id, 1, "acao__mad_max", "Mad Max")
        _add_vote(p2.id, 1, "acao__mad_max", "Mad Max")
        db.session.commit()
        p1_id = p1.id

    client = app.test_client()
    client.set_cookie("player_id", str(p1_id))
    with capture_context(app) as ctx:
        resp = client.get("/results")

    assert resp.status_code == 200
    movies = ctx["match_data"]["movies"]
    mad_max = next(m for m in movies if m["movie_id"] == "acao__mad_max")
    assert "poster" not in mad_max


# ── Cycle 6: year injetado a partir de MOVIE_LOOKUP ──────────────────────────

def test_year_injected_from_movie_lookup(app, monkeypatch):
    import routes.game as gm
    monkeypatch.setattr(gm, "_manifest", FAKE_MANIFEST)

    with app.app_context():
        s = Session.query.first()
        _set_final(s, result_round=1)
        p1 = _add_player(s.id, "Alice")
        p2 = _add_player(s.id, "Bob")
        # "acao__die_hard" existe no MOVIE_LOOKUP com year=1988
        _add_vote(p1.id, 1, "acao__die_hard", "Die Hard")
        _add_vote(p2.id, 1, "acao__die_hard", "Die Hard")
        db.session.commit()

    client = app.test_client()
    with capture_context(app) as ctx:
        client.get("/desktop")

    movies = ctx["match_data"]["movies"]
    die_hard = next(m for m in movies if m["movie_id"] == "acao__die_hard")
    assert die_hard.get("year") == 1988


# ── Cycle 7: módulo match permanece puro ─────────────────────────────────────

def test_match_module_has_no_manifest_import():
    import ast, pathlib
    src = pathlib.Path(__file__).parent.parent / "match.py"
    tree = ast.parse(src.read_text())
    imports = [
        node.names[0].name if isinstance(node, ast.Import) else node.module
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
    ]
    assert not any("manifest" in (imp or "") for imp in imports)
    assert not any("posters" in (imp or "") for imp in imports)
    assert not any("json" in (imp or "") for imp in imports)
