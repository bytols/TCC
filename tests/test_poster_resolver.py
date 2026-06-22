"""Unit tests for classify_tmdb_result — no network, no disk."""
import pytest
from resolve_posters import classify_tmdb_result


def _result(tmdb_id=1, year=2001, poster="/p.jpg"):
    """Helper to build a minimal TMDB result dict."""
    release_date = f"{year}-06-15" if year else ""
    return {
        "id": tmdb_id,
        "title": "Some Movie",
        "release_date": release_date,
        "poster_path": poster,
    }


# --- Tracer bullet ---

def test_exact_year_single_result_is_accepted():
    results = [_result(tmdb_id=42, year=2001)]
    out = classify_tmdb_result(expected_year=2001, results=results)
    assert out["status"] == "accept"
    assert out["match"]["tmdb_id"] == 42
    assert out["match"]["poster_path"] == "/p.jpg"


# --- Orphan cases ---

def test_no_results_is_orphan():
    out = classify_tmdb_result(expected_year=2001, results=[])
    assert out["status"] == "orphan"
    assert out["match"] is None


def test_single_result_without_poster_is_orphan():
    result = _result(year=2001, poster=None)
    out = classify_tmdb_result(expected_year=2001, results=[result])
    assert out["status"] == "orphan"


def test_empty_poster_path_is_orphan():
    result = _result(year=2001, poster="")
    out = classify_tmdb_result(expected_year=2001, results=[result])
    assert out["status"] == "orphan"


# --- Review cases ---

def test_year_diverges_is_review():
    results = [_result(tmdb_id=99, year=2005)]
    out = classify_tmdb_result(expected_year=2001, results=results)
    assert out["status"] == "review"
    assert out["match"] is None


def test_multiple_candidates_same_year_is_review():
    results = [
        _result(tmdb_id=1, year=2001),
        _result(tmdb_id=2, year=2001),
    ]
    out = classify_tmdb_result(expected_year=2001, results=results)
    assert out["status"] == "review"


def test_one_exact_one_diverging_accepts_the_exact():
    """If one result matches the year and others don't, still auto-accept."""
    results = [
        _result(tmdb_id=7, year=2001),
        _result(tmdb_id=8, year=1999),
    ]
    out = classify_tmdb_result(expected_year=2001, results=results)
    assert out["status"] == "accept"
    assert out["match"]["tmdb_id"] == 7


def test_missing_release_date_treated_as_year_mismatch():
    result = {
        "id": 5,
        "title": "Unknown Date",
        "release_date": "",
        "poster_path": "/p.jpg",
    }
    out = classify_tmdb_result(expected_year=2001, results=[result])
    assert out["status"] == "review"
