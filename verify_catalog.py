"""
Verify which catalog movies are missing a resolved poster.

Usage:
    python verify_catalog.py [--manifest PATH]

    --manifest PATH   path to posters.json (default: data/posters.json)

Exits with code 1 if any movies are missing, 0 otherwise.
"""
from __future__ import annotations

import json
import sys


def missing_posters(catalog: dict, manifest: dict) -> list[str]:
    """Return movie IDs present in catalog but absent from manifest."""
    all_ids = [
        movie["id"]
        for cat in catalog.values()
        for movie in cat["movies"]
    ]
    return [mid for mid in all_ids if mid not in manifest]


def _main(argv: list[str] | None = None) -> int:
    import argparse
    from data.movies import MOVIES

    parser = argparse.ArgumentParser(description="Verify poster manifest coverage")
    parser.add_argument("--manifest", default="data/posters.json",
                        help="Path to posters.json (default: data/posters.json)")
    args = parser.parse_args(argv)

    try:
        with open(args.manifest, encoding="utf-8") as fh:
            manifest = json.load(fh)
    except FileNotFoundError:
        manifest = {}

    missing = missing_posters(MOVIES, manifest)

    if not missing:
        print("OK — all catalog movies have a verified poster.")
        return 0

    print(f"{len(missing)} movie(s) without a verified poster:\n")
    for mid in missing:
        print(f"  {mid}")
    return 1


if __name__ == "__main__":
    sys.exit(_main())
