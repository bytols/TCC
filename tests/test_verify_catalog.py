"""Unit tests for missing_posters — no IO, no network."""
import pytest
from verify_catalog import missing_posters


# Minimal catalog fixture: two categories, three movies total
CATALOG = {
    "acao": {
        "label": "AÇÃO",
        "color": "#E74C3C",
        "movies": [
            {"id": "acao__m1", "title": "Movie 1", "year": 2001},
            {"id": "acao__m2", "title": "Movie 2", "year": 2002},
        ],
    },
    "drama": {
        "label": "DRAMA",
        "color": "#3498DB",
        "movies": [
            {"id": "drama__m3", "title": "Movie 3", "year": 2003},
        ],
    },
}


# --- Tracer bullet ---

def test_movie_absent_from_manifest_is_returned():
    manifest = {}  # nothing resolved yet
    result = missing_posters(CATALOG, manifest)
    assert "acao__m1" in result
    assert "acao__m2" in result
    assert "drama__m3" in result


# --- Happy path ---

def test_all_covered_returns_empty_list():
    manifest = {
        "acao__m1": {"tmdb_id": 1, "file": "static/img/posters/acao__m1.jpg"},
        "acao__m2": {"tmdb_id": 2, "file": "static/img/posters/acao__m2.jpg"},
        "drama__m3": {"tmdb_id": 3, "file": "static/img/posters/drama__m3.jpg"},
    }
    result = missing_posters(CATALOG, manifest)
    assert result == []


# --- Partial coverage ---

def test_only_missing_ids_are_returned():
    manifest = {
        "acao__m1": {"tmdb_id": 1, "file": "static/img/posters/acao__m1.jpg"},
    }
    result = missing_posters(CATALOG, manifest)
    assert "acao__m1" not in result
    assert "acao__m2" in result
    assert "drama__m3" in result


# --- Manifest with extra keys doesn't pollute result ---

def test_extra_manifest_keys_ignored():
    manifest = {
        "acao__m1": {"tmdb_id": 1, "file": "static/img/posters/acao__m1.jpg"},
        "acao__m2": {"tmdb_id": 2, "file": "static/img/posters/acao__m2.jpg"},
        "drama__m3": {"tmdb_id": 3, "file": "static/img/posters/drama__m3.jpg"},
        "orphan__not_in_catalog": {"tmdb_id": 99, "file": "static/img/posters/x.jpg"},
    }
    result = missing_posters(CATALOG, manifest)
    assert result == []


# --- Return type ---

def test_returns_list():
    result = missing_posters(CATALOG, {})
    assert isinstance(result, list)
