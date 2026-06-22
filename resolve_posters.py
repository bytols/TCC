"""
Build script: resolve TMDB posters for all movies in data/movies.py.

Usage:
    TMDB_API_KEY=xxx python resolve_posters.py [--dry-run]

Outputs:
    data/posters.json       — manifest {movie_id: {tmdb_id, file}}
    data/review_list.json   — ambiguous matches needing human sign-off
    static/img/posters/     — downloaded JPG posters
    stdout                  — failure report by category
"""
from __future__ import annotations

import json
import os
import sys
import urllib.parse
import urllib.request


# ---------------------------------------------------------------------------
# Pure classification logic (testable without network or disk)
# ---------------------------------------------------------------------------

def classify_tmdb_result(expected_year: int, results: list[dict]) -> dict:
    """
    Classify TMDB search results for a single movie.

    Rules:
      - No results with poster_path → orphan
      - Exactly 1 result with poster AND year matches expected_year → accept
      - Year diverges OR multiple year-matching candidates → review

    Returns:
        {"status": "accept"|"review"|"orphan", "match": dict|None, "reason": str}
    """
    with_poster = [r for r in results if r.get("poster_path")]
    if not with_poster:
        return {"status": "orphan", "match": None, "reason": "no poster in results"}

    def _year(r: dict) -> int | None:
        rd = r.get("release_date") or ""
        return int(rd[:4]) if len(rd) >= 4 else None

    year_exact = [r for r in with_poster if _year(r) == expected_year]

    if len(year_exact) == 1:
        r = year_exact[0]
        return {
            "status": "accept",
            "match": {"tmdb_id": r["id"], "poster_path": r["poster_path"]},
            "reason": "exact year match",
        }

    if len(year_exact) > 1:
        return {"status": "review", "match": None, "reason": "multiple candidates with same year"}

    # No year-exact matches among poster results → year diverges
    return {"status": "review", "match": None, "reason": "year diverges"}


# ---------------------------------------------------------------------------
# Network boundary (mocked in tests)
# ---------------------------------------------------------------------------

def search_tmdb(title: str, year: int | None = None) -> list[dict]:
    """Search TMDB for a movie. Returns raw results list."""
    api_key = os.environ.get("TMDB_API_KEY", "")
    params: dict = {
        "api_key": api_key,
        "query": title,
        "language": "pt-BR",
        "include_adult": "false",
    }
    if year:
        params["primary_release_year"] = str(year)
    url = "https://api.themoviedb.org/3/search/movie?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=6) as resp:
            data = json.loads(resp.read().decode())
        return data.get("results", [])
    except Exception as exc:
        print(f"  [WARN] TMDB search failed: {exc}", file=sys.stderr)
        return []


def download_poster(poster_path: str, dest: str) -> bool:
    """Download a TMDB poster image to dest. Returns True on success."""
    url = "https://image.tmdb.org/t/p/w500" + poster_path
    try:
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        urllib.request.urlretrieve(url, dest)
        return True
    except Exception as exc:
        print(f"  [WARN] Download failed {url}: {exc}", file=sys.stderr)
        return False


# ---------------------------------------------------------------------------
# Main resolver
# ---------------------------------------------------------------------------

def resolve_all(
    movies: dict,
    posters_dir: str = "static/img/posters",
    *,
    dry_run: bool = False,
) -> tuple[dict, list[dict], dict[str, list[str]]]:
    """
    Resolve posters for all movies.

    Returns:
        manifest      — {movie_id: {tmdb_id, file}}
        review_list   — [{movie_id, title, year, category, candidates, reason}]
        failures      — {category_label: [movie_id, ...]}  (orphans + errors)
    """
    manifest: dict = {}
    review_list: list[dict] = []
    failures: dict[str, list[str]] = {}

    for category_key, cat_data in movies.items():
        label = cat_data["label"]
        for movie in cat_data["movies"]:
            movie_id = movie["id"]
            title = movie["title"]
            year = movie.get("year")

            print(f"  {movie_id} ({year}) ...", end=" ", flush=True)

            # First attempt: pt-BR title + year
            results = search_tmdb(title, year)
            verdict = classify_tmdb_result(year, results)

            # Fallback: search without year restriction
            if verdict["status"] == "orphan" and year:
                results2 = search_tmdb(title)
                verdict = classify_tmdb_result(year, results2)

            if verdict["status"] == "accept":
                match = verdict["match"]
                dest = os.path.join(posters_dir, f"{movie_id}.jpg")
                if not dry_run:
                    ok = download_poster(match["poster_path"], dest)
                    if not ok:
                        failures.setdefault(label, []).append(movie_id)
                        print("DL-FAIL")
                        continue
                manifest[movie_id] = {"tmdb_id": match["tmdb_id"], "file": dest}
                print("OK")

            elif verdict["status"] == "review":
                review_list.append({
                    "movie_id": movie_id,
                    "title": title,
                    "year": year,
                    "category": label,
                    "reason": verdict["reason"],
                    "candidates": [
                        {
                            "tmdb_id": r["id"],
                            "title": r.get("title"),
                            "release_date": r.get("release_date"),
                            "poster_path": r.get("poster_path"),
                        }
                        for r in results
                        if r.get("poster_path")
                    ][:5],
                })
                failures.setdefault(label, []).append(movie_id)
                print("REVIEW")

            else:  # orphan
                failures.setdefault(label, []).append(movie_id)
                print("ORPHAN")

    return manifest, review_list, failures


def _print_report(failures: dict[str, list[str]]) -> None:
    print("\n=== Failure report by category ===")
    if not failures:
        print("  All movies resolved!")
        return
    for label, ids in sorted(failures.items()):
        print(f"  {label}: {len(ids)} unresolved")
        for mid in ids:
            print(f"    - {mid}")


def _write_json(path: str, data: object) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    import argparse
    from data.movies import MOVIES

    parser = argparse.ArgumentParser(description="Resolve TMDB posters for the RUÍDO catalog.")
    parser.add_argument("--dry-run", action="store_true", help="Skip downloads and disk writes")
    args = parser.parse_args()

    if not os.environ.get("TMDB_API_KEY"):
        print("ERROR: TMDB_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    print("Resolving posters...")
    manifest, review_list, failures = resolve_all(MOVIES, dry_run=args.dry_run)
    _print_report(failures)

    if not args.dry_run:
        _write_json("data/posters.json", manifest)
        print(f"\nManifest: data/posters.json ({len(manifest)} entries)")
        _write_json("data/review_list.json", review_list)
        print(f"Review list: data/review_list.json ({len(review_list)} entries)")
    else:
        print(f"\n[dry-run] Would write {len(manifest)} manifest entries, {len(review_list)} review entries")
