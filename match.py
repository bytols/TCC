from collections import defaultdict


def calculate_match(votes: list[dict]) -> dict:
    """
    votes: list of {player_id, movie_id, movie_title, category, player_name}
    Returns match statistics for the given round votes.
    """
    per_movie: dict[str, list] = defaultdict(list)
    movie_meta: dict[str, dict] = {}

    for v in votes:
        per_movie[v["movie_id"]].append({"id": v["player_id"], "name": v.get("player_name", "")})
        if v["movie_id"] not in movie_meta:
            movie_meta[v["movie_id"]] = {
                "movie_id": v["movie_id"],
                "movie_title": v["movie_title"],
                "category": v["category"],
            }

    unique_movies = list(per_movie.keys())
    matched_movies = [m for m, players in per_movie.items() if len(players) >= 2]

    total_unique = len(unique_movies)
    match_pct = round(len(matched_movies) / total_unique * 100, 1) if total_unique > 0 else 0.0

    movies_display = []
    for movie_id, players in per_movie.items():
        meta = movie_meta[movie_id]
        movies_display.append({
            **meta,
            "players": players,
            "is_match": len(players) >= 2,
            "count": len(players),
        })
    movies_display.sort(key=lambda x: -x["count"])

    return {
        "match_pct": match_pct,
        "matched_count": len(matched_movies),
        "total_unique": total_unique,
        "movies": movies_display,
    }
