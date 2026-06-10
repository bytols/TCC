"""
Busca de posters de filmes via TMDB (The Movie Database).

A chave fica em variável de ambiente `TMDB_API_KEY` (carregada de `.env`,
ver `.env.example`). Sem chave, `get_poster_url` devolve `None` e a UI cai no
placeholder (gradiente + inicial do título).

Os resultados são cacheados em memória e persistidos em `poster_cache.json`
(na raiz do projeto) para evitar re-buscas entre reinícios.
"""
import os
import json
import urllib.parse
import urllib.request

import config

_CACHE_PATH = os.path.join(os.path.dirname(__file__), "poster_cache.json")
_IMG_BASE = "https://image.tmdb.org/t/p/w500"

try:
    with open(_CACHE_PATH, encoding="utf-8") as f:
        _cache = json.load(f)
except (OSError, ValueError):
    _cache = {}


def _save_cache() -> None:
    try:
        with open(_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(_cache, f, ensure_ascii=False)
    except OSError:
        pass


def is_configured() -> bool:
    return bool(config.TMDB_API_KEY)


def _fetch_from_tmdb(title: str, year=None) -> str | None:
    params = {
        "api_key": config.TMDB_API_KEY,
        "query": title,
        "language": "pt-BR",
        "include_adult": "false",
    }
    if year:
        params["year"] = str(year)
    url = "https://api.themoviedb.org/3/search/movie?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=4) as resp:
            data = json.loads(resp.read().decode())
    except Exception:
        return None
    for result in data.get("results", []):
        if result.get("poster_path"):
            return _IMG_BASE + result["poster_path"]
    return None


def get_poster_url(movie_id: str, title: str, year=None) -> str | None:
    """URL do poster (w500) ou None. Cacheado por `movie_id`.
    `None` é cacheado também (com sentinela) para não re-bater na API."""
    if movie_id in _cache:
        return _cache[movie_id] or None
    if not is_configured():
        return None
    url = _fetch_from_tmdb(title, year)
    _cache[movie_id] = url or ""
    _save_cache()
    return url
