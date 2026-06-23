"""
Slice TV 2 — Reconstrução da tela final desktop (3 zonas + CSS do Figma).

Testa o layout de 3 zonas (esquerda / centro / direita) + rodapé do Figma 254-5321.
Os testes de classes de infra já passam (test_slice_final_tv_layout.py, test_slice_final_time_avatars.py);
este arquivo cobre os comportamentos novos desta slice.
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


def _set_final(session, result_round=1, result_seconds=120):
    session.state = "FINAL"
    session.result_round = result_round
    session.result_seconds = result_seconds
    db.session.flush()


def _html_final(app, monkeypatch, *, result_seconds=120, movies=None):
    """Helper: sets session to FINAL with 2 players and given consensus movies."""
    import routes.game as gm
    monkeypatch.setattr(gm, "_manifest", {})
    if movies is None:
        movies = [("acao__die_hard", "Die Hard")]
    with app.app_context():
        s = Session.query.first()
        _set_final(s, result_round=1, result_seconds=result_seconds)
        p1 = _add_player(s.id, "Alice")
        p2 = _add_player(s.id, "Bob")
        for movie_id, title in movies:
            _add_vote(p1.id, 1, movie_id, title)
            _add_vote(p2.id, 1, movie_id, title)
        db.session.commit()
    return app.test_client().get("/desktop").data.decode()


# ── Cycle 1: zona direita com label "FILME ESCOLHIDO" ────────────────────────

def test_final_right_zone_exists(app, monkeypatch):
    html = _html_final(app, monkeypatch)
    assert "final-right" in html


def test_final_right_has_filme_escolhido_label(app, monkeypatch):
    html = _html_final(app, monkeypatch)
    assert "FILME ESCOLHIDO" in html


# ── Cycle 2: ano do filme renderizado na zona direita ────────────────────────

def test_final_right_shows_year(app, monkeypatch):
    # Die Hard year = 1988 (from MOVIE_LOOKUP)
    html = _html_final(app, monkeypatch, movies=[("acao__die_hard", "Die Hard")])
    assert "1988" in html


# ── Cycle 3: gênero (category_label) renderizado na zona direita ─────────────

def test_final_right_shows_genre(app, monkeypatch):
    # Die Hard category_label = "AÇÃO"
    html = _html_final(app, monkeypatch, movies=[("acao__die_hard", "Die Hard")])
    assert "AÇÃO" in html


# ── Cycle 4: rodapé com tagline ──────────────────────────────────────────────

def test_final_footer_exists(app, monkeypatch):
    html = _html_final(app, monkeypatch)
    assert "final-footer" in html


def test_final_footer_has_tagline(app, monkeypatch):
    html = _html_final(app, monkeypatch)
    assert "Jam de Filmes" in html


# ── Cycle 5: wordmark RUÍDO no rodapé ────────────────────────────────────────

def test_final_footer_has_wordmark(app, monkeypatch):
    html = _html_final(app, monkeypatch)
    assert "final-footer" in html
    assert "logo.png" in html
