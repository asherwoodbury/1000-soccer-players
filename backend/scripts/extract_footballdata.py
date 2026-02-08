#!/usr/bin/env python3
"""
Generic data extraction tool for football-data.org's free API.

Self-contained script with no project imports - copy-pasteable into other projects.
Stores raw API responses and parsed structured data in a separate SQLite database.

Usage:
    python3 extract_footballdata.py sync-teams --competitions PL --seasons 2024
    python3 extract_footballdata.py sync-matches --competitions PL --seasons 2024
    python3 extract_footballdata.py sync-lineups --competitions PL --seasons 2024
    python3 extract_footballdata.py sync-all --competitions PL --seasons 2024
    python3 extract_footballdata.py stats
"""

import argparse
import hashlib
import json
import os
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BASE_URL = "https://api.football-data.org/v4"

DEFAULT_DB_PATH = str(Path(__file__).parent.parent / "data" / "footballdata.db")

FREE_TIER_COMPETITIONS = [
    "PL", "BL1", "PD", "SA", "FL1", "DED", "PPL", "ELC", "BSA", "CL", "WC", "EC",
]

DEFAULT_SEASONS = list(range(2021, 2026))

# ---------------------------------------------------------------------------
# Database setup
# ---------------------------------------------------------------------------

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS api_responses (
    id INTEGER PRIMARY KEY,
    endpoint TEXT NOT NULL,
    params TEXT NOT NULL,
    params_hash TEXT NOT NULL UNIQUE,
    response_json TEXT NOT NULL,
    http_status INTEGER NOT NULL,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS competitions (
    id INTEGER PRIMARY KEY,
    code TEXT UNIQUE,
    name TEXT,
    area_name TEXT
);

CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY,
    name TEXT,
    short_name TEXT,
    tla TEXT,
    crest_url TEXT,
    area_name TEXT
);

CREATE TABLE IF NOT EXISTS team_competitions (
    team_id INTEGER NOT NULL,
    competition_id INTEGER NOT NULL,
    season INTEGER NOT NULL,
    UNIQUE(team_id, competition_id, season)
);

CREATE TABLE IF NOT EXISTS persons (
    id INTEGER PRIMARY KEY,
    name TEXT,
    first_name TEXT,
    last_name TEXT,
    date_of_birth TEXT,
    nationality TEXT,
    position TEXT
);

CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY,
    competition_id INTEGER,
    season INTEGER,
    matchday INTEGER,
    utc_date TEXT,
    home_team_id INTEGER,
    away_team_id INTEGER,
    home_score INTEGER,
    away_score INTEGER,
    status TEXT
);

CREATE TABLE IF NOT EXISTS match_lineups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id INTEGER NOT NULL,
    person_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    competition_id INTEGER,
    season INTEGER,
    lineup_type TEXT,
    shirt_number INTEGER,
    UNIQUE(match_id, person_id)
);

CREATE TABLE IF NOT EXISTS sync_status (
    competition_code TEXT NOT NULL,
    season INTEGER NOT NULL,
    step TEXT NOT NULL,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(competition_code, season, step)
);

CREATE INDEX IF NOT EXISTS idx_api_responses_hash ON api_responses(params_hash);
CREATE INDEX IF NOT EXISTS idx_matches_comp_season ON matches(competition_id, season);
CREATE INDEX IF NOT EXISTS idx_match_lineups_match ON match_lineups(match_id);
CREATE INDEX IF NOT EXISTS idx_match_lineups_person ON match_lineups(person_id);
"""


def init_db(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    return conn


# ---------------------------------------------------------------------------
# API key resolution
# ---------------------------------------------------------------------------

def resolve_api_key(cli_key: str | None) -> str:
    if cli_key:
        return cli_key

    env_key = os.environ.get("FOOTBALL_DATA_API_KEY")
    if env_key:
        return env_key

    # Try .env file in project root
    env_file = Path(__file__).resolve().parent.parent.parent / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line.startswith("FOOTBALL_DATA_API_KEY="):
                val = line.split("=", 1)[1].strip().strip("\"'")
                if val:
                    return val

    print("Error: No API key found.")
    print("Provide via --api-key, FOOTBALL_DATA_API_KEY env var, or .env file.")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Rate limiter
# ---------------------------------------------------------------------------

class RateLimiter:
    """Sliding window rate limiter: max_requests per window_seconds."""

    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.timestamps: list[float] = []

    def wait_if_needed(self):
        now = time.time()
        cutoff = now - self.window_seconds
        self.timestamps = [t for t in self.timestamps if t > cutoff]

        if len(self.timestamps) >= self.max_requests:
            sleep_time = self.timestamps[0] - cutoff + 0.1
            if sleep_time > 0:
                print(f"  Rate limit: sleeping {sleep_time:.1f}s...")
                time.sleep(sleep_time)

        self.timestamps.append(time.time())


# ---------------------------------------------------------------------------
# API request with caching
# ---------------------------------------------------------------------------

def make_params_hash(endpoint: str, params: dict) -> str:
    key = endpoint + "|" + json.dumps(params, sort_keys=True)
    return hashlib.sha256(key.encode()).hexdigest()


def get_cached_response(conn: sqlite3.Connection, params_hash: str) -> dict | None:
    row = conn.execute(
        "SELECT response_json, http_status FROM api_responses WHERE params_hash = ?",
        (params_hash,),
    ).fetchone()
    if row:
        return {"body": json.loads(row[0]), "status": row[1]}
    return None


def store_response(conn: sqlite3.Connection, endpoint: str, params: dict,
                   params_hash: str, response_json: str, http_status: int):
    conn.execute(
        """INSERT OR REPLACE INTO api_responses
           (endpoint, params, params_hash, response_json, http_status, fetched_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (endpoint, json.dumps(params, sort_keys=True), params_hash,
         response_json, http_status, datetime.utcnow().isoformat()),
    )
    conn.commit()


def api_request(conn: sqlite3.Connection, endpoint: str, params: dict,
                api_key: str, rate_limiter: RateLimiter, max_retries: int = 3) -> dict | None:
    """
    Fetch from football-data.org with caching, rate limiting, and retry.
    Returns parsed JSON body or None on error.
    """
    params_hash = make_params_hash(endpoint, params)

    cached = get_cached_response(conn, params_hash)
    if cached:
        if cached["status"] == 200:
            return cached["body"]
        # Non-200 cached responses (404, 403) - don't retry
        return None

    url = f"{BASE_URL}{endpoint}"
    if params:
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{url}?{query_string}"

    for attempt in range(max_retries):
        rate_limiter.wait_if_needed()

        try:
            req = Request(url)
            req.add_header("X-Auth-Token", api_key)
            with urlopen(req, timeout=30) as resp:
                body = resp.read().decode("utf-8")
                store_response(conn, endpoint, params, params_hash, body, resp.status)
                return json.loads(body)

        except HTTPError as e:
            body = ""
            try:
                body = e.read().decode("utf-8")
            except Exception:
                pass

            if e.code == 429:
                wait = 65 * (attempt + 1)
                print(f"  429 Too Many Requests. Waiting {wait}s (attempt {attempt + 1}/{max_retries})...")
                time.sleep(wait)
                continue

            # Store non-retryable errors in cache so we don't re-fetch
            store_response(conn, endpoint, params, params_hash, body or "{}", e.code)
            if e.code == 404:
                return None
            if e.code == 403:
                print(f"  403 Forbidden: {endpoint} (may not be available on free tier)")
                return None
            print(f"  HTTP {e.code}: {endpoint}")
            return None

        except (URLError, TimeoutError) as e:
            print(f"  Network error (attempt {attempt + 1}/{max_retries}): {e}")
            time.sleep(10 * (attempt + 1))

    print(f"  Failed after {max_retries} retries: {endpoint}")
    return None


# ---------------------------------------------------------------------------
# Parsers - extract structured data from raw API JSON
# ---------------------------------------------------------------------------

def parse_competition(conn: sqlite3.Connection, data: dict):
    comp = data.get("competition", data)
    if not comp.get("id"):
        return
    conn.execute(
        "INSERT OR REPLACE INTO competitions (id, code, name, area_name) VALUES (?, ?, ?, ?)",
        (comp["id"], comp.get("code"), comp.get("name"),
         comp.get("area", {}).get("name")),
    )


def parse_teams(conn: sqlite3.Connection, data: dict, competition_id: int, season: int):
    person_count = 0
    for team in data.get("teams", []):
        conn.execute(
            """INSERT OR REPLACE INTO teams (id, name, short_name, tla, crest_url, area_name)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (team["id"], team.get("name"), team.get("shortName"),
             team.get("tla"), team.get("crest"), team.get("area", {}).get("name")),
        )
        conn.execute(
            "INSERT OR IGNORE INTO team_competitions (team_id, competition_id, season) VALUES (?, ?, ?)",
            (team["id"], competition_id, season),
        )
        # Extract squad members as persons
        for player in team.get("squad", []):
            pid = player.get("id")
            if not pid:
                continue
            conn.execute(
                """INSERT OR REPLACE INTO persons (id, name, first_name, last_name,
                   date_of_birth, nationality, position)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (pid, player.get("name"), None, None,
                 player.get("dateOfBirth"), player.get("nationality"),
                 player.get("position")),
            )
            person_count += 1
    return person_count


def parse_matches(conn: sqlite3.Connection, data: dict, competition_id: int, season: int):
    for match in data.get("matches", []):
        home_id = match.get("homeTeam", {}).get("id")
        away_id = match.get("awayTeam", {}).get("id")
        score = match.get("score", {})
        ft = score.get("fullTime", {})
        conn.execute(
            """INSERT OR REPLACE INTO matches
               (id, competition_id, season, matchday, utc_date, home_team_id, away_team_id,
                home_score, away_score, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (match["id"], competition_id, season, match.get("matchday"),
             match.get("utcDate"), home_id, away_id,
             ft.get("home"), ft.get("away"), match.get("status")),
        )


def parse_lineups(conn: sqlite3.Connection, match_data: dict):
    match_id = match_data.get("id")
    comp_id = match_data.get("competition", {}).get("id")
    season_year = match_data.get("season", {}).get("startDate", "")[:4]
    season = int(season_year) if season_year else None

    for side in ("homeTeam", "awayTeam"):
        team_info = match_data.get(side, {})
        team_id = team_info.get("id")
        if not team_id:
            continue

        for lineup_type, player_list in (("starting", team_info.get("lineup", [])),
                                          ("bench", team_info.get("bench", []))):
            for player in (player_list or []):
                pid = player.get("id")
                if not pid:
                    continue
                conn.execute(
                    """INSERT OR REPLACE INTO persons (id, name, first_name, last_name,
                       date_of_birth, nationality, position)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (pid, player.get("name"), None, None,
                     player.get("dateOfBirth"), player.get("nationality"),
                     player.get("position")),
                )
                conn.execute(
                    """INSERT OR IGNORE INTO match_lineups
                       (match_id, person_id, team_id, competition_id, season, lineup_type, shirt_number)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (match_id, pid, team_id, comp_id, season, lineup_type,
                     player.get("shirtNumber")),
                )


# ---------------------------------------------------------------------------
# Sync functions
# ---------------------------------------------------------------------------

def is_step_complete(conn: sqlite3.Connection, code: str, season: int, step: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sync_status WHERE competition_code=? AND season=? AND step=?",
        (code, season, step),
    ).fetchone()
    return row is not None


def mark_step_complete(conn: sqlite3.Connection, code: str, season: int, step: str):
    conn.execute(
        "INSERT OR IGNORE INTO sync_status (competition_code, season, step, completed_at) VALUES (?, ?, ?, ?)",
        (code, season, step, datetime.utcnow().isoformat()),
    )
    conn.commit()


def _check_cached_403(conn: sqlite3.Connection, endpoint: str, params: dict) -> bool:
    """Check if this endpoint+params is cached as a 403 (free tier limitation)."""
    ph = make_params_hash(endpoint, params)
    cached = get_cached_response(conn, ph)
    return cached is not None and cached["status"] == 403


def sync_teams(conn: sqlite3.Connection, api_key: str, rate_limiter: RateLimiter,
               competitions: list[str], seasons: list[int]):
    print("\n=== Syncing teams ===")
    # Process newest seasons first - older ones are more likely to 403
    sorted_seasons = sorted(seasons, reverse=True)
    total = len(competitions) * len(sorted_seasons)
    done = 0
    api_calls = 0

    for code in competitions:
        consecutive_403s = 0
        for season in sorted_seasons:
            done += 1
            if is_step_complete(conn, code, season, "teams"):
                continue

            # If we've hit 2 consecutive 403s going backward, skip remaining older seasons
            if consecutive_403s >= 2:
                mark_step_complete(conn, code, season, "teams")
                continue

            endpoint = f"/competitions/{code}/teams"
            params = {"season": str(season)}
            params_hash = make_params_hash(endpoint, params)
            was_cached = get_cached_response(conn, params_hash) is not None

            # Check if already cached as 403 before making a request
            if _check_cached_403(conn, endpoint, params):
                mark_step_complete(conn, code, season, "teams")
                consecutive_403s += 1
                continue

            data = api_request(conn, endpoint, params, api_key, rate_limiter)
            if not was_cached:
                api_calls += 1

            if data and "teams" in data:
                consecutive_403s = 0
                parse_competition(conn, data)
                comp_id = data.get("competition", {}).get("id")
                if comp_id:
                    persons = parse_teams(conn, data, comp_id, season)
                    conn.commit()
                mark_step_complete(conn, code, season, "teams")
                print(f"  [{done}/{total}] {code} {season}: {len(data['teams'])} teams, {persons} players")
            else:
                consecutive_403s += 1
                mark_step_complete(conn, code, season, "teams")
                if consecutive_403s == 2:
                    print(f"  [{done}/{total}] {code}: skipping older seasons (403 - free tier limit)")

    print(f"  Teams sync complete. API calls: {api_calls}")


def reparse_teams(conn: sqlite3.Connection):
    """Re-parse all cached team responses to extract squad/person data."""
    rows = conn.execute(
        "SELECT response_json FROM api_responses WHERE endpoint LIKE '%/teams' AND http_status = 200"
    ).fetchall()
    total_persons = 0
    for (raw,) in rows:
        data = json.loads(raw)
        comp_id = data.get("competition", {}).get("id")
        season_info = data.get("season", {})
        season = int(season_info.get("startDate", "0")[:4]) if season_info.get("startDate") else None
        if comp_id and season:
            total_persons += parse_teams(conn, data, comp_id, season)
    conn.commit()
    return len(rows), total_persons


def sync_matches(conn: sqlite3.Connection, api_key: str, rate_limiter: RateLimiter,
                 competitions: list[str], seasons: list[int]):
    print("\n=== Syncing matches ===")
    sorted_seasons = sorted(seasons, reverse=True)
    total = len(competitions) * len(sorted_seasons)
    done = 0
    api_calls = 0

    for code in competitions:
        consecutive_403s = 0
        for season in sorted_seasons:
            done += 1
            if is_step_complete(conn, code, season, "matches"):
                continue

            if consecutive_403s >= 2:
                mark_step_complete(conn, code, season, "matches")
                continue

            endpoint = f"/competitions/{code}/matches"
            params = {"season": str(season)}
            params_hash = make_params_hash(endpoint, params)
            was_cached = get_cached_response(conn, params_hash) is not None

            if _check_cached_403(conn, endpoint, params):
                mark_step_complete(conn, code, season, "matches")
                consecutive_403s += 1
                continue

            data = api_request(conn, endpoint, params, api_key, rate_limiter)
            if not was_cached:
                api_calls += 1

            if data and "matches" in data:
                consecutive_403s = 0
                parse_competition(conn, data)
                comp_id = data.get("competition", {}).get("id")
                if comp_id:
                    parse_matches(conn, data, comp_id, season)
                    conn.commit()
                match_count = len(data.get("matches", []))
                mark_step_complete(conn, code, season, "matches")
                print(f"  [{done}/{total}] {code} {season}: {match_count} matches")
            else:
                consecutive_403s += 1
                mark_step_complete(conn, code, season, "matches")
                if consecutive_403s == 2:
                    print(f"  [{done}/{total}] {code}: skipping older seasons (403 - free tier limit)")

    print(f"  Matches sync complete. API calls: {api_calls}")


def sync_lineups(conn: sqlite3.Connection, api_key: str, rate_limiter: RateLimiter,
                 competitions: list[str], seasons: list[int]):
    print("\n=== Syncing lineups ===")

    # Build filter for competition IDs from the codes we care about
    comp_ids = []
    for code in competitions:
        row = conn.execute("SELECT id FROM competitions WHERE code = ?", (code,)).fetchone()
        if row:
            comp_ids.append(row[0])

    if not comp_ids:
        print("  No competitions found in database. Run sync-teams first.")
        return

    # Find finished matches without lineup data
    placeholders = ",".join("?" * len(comp_ids))
    season_filter = ""
    query_params: list = list(comp_ids)
    if seasons != DEFAULT_SEASONS:
        season_placeholders = ",".join("?" * len(seasons))
        season_filter = f"AND m.season IN ({season_placeholders})"
        query_params.extend(seasons)

    rows = conn.execute(f"""
        SELECT m.id FROM matches m
        LEFT JOIN match_lineups ml ON m.id = ml.match_id
        WHERE m.competition_id IN ({placeholders})
        {season_filter}
        AND m.status = 'FINISHED'
        AND ml.id IS NULL
        ORDER BY m.id
    """, query_params).fetchall()

    match_ids = [r[0] for r in rows]

    # Also exclude matches we already fetched but had no lineup data
    # (cached as non-200 or empty lineups)
    already_attempted = set()
    for mid in match_ids:
        endpoint = f"/matches/{mid}"
        ph = make_params_hash(endpoint, {})
        if get_cached_response(conn, ph) is not None:
            already_attempted.add(mid)

    remaining = [mid for mid in match_ids if mid not in already_attempted]

    # For already-attempted matches that are cached with 200, try parsing them
    for mid in already_attempted:
        endpoint = f"/matches/{mid}"
        ph = make_params_hash(endpoint, {})
        cached = get_cached_response(conn, ph)
        if cached and cached["status"] == 200:
            parse_lineups(conn, cached["body"])
    conn.commit()

    total = len(remaining)
    if total == 0:
        print(f"  No new matches to fetch lineups for. ({len(already_attempted)} already cached)")
        return

    print(f"  {total} matches need lineup data ({len(already_attempted)} already cached)")
    api_calls = 0
    lineups_found = 0

    for i, match_id in enumerate(remaining, 1):
        endpoint = f"/matches/{match_id}"
        data = api_request(conn, endpoint, {}, api_key, rate_limiter)
        api_calls += 1

        if data:
            home_lineup = data.get("homeTeam", {}).get("lineup", [])
            away_lineup = data.get("awayTeam", {}).get("lineup", [])
            if home_lineup or away_lineup:
                parse_lineups(conn, data)
                lineups_found += 1

        if i % 10 == 0:
            conn.commit()
            print(f"  [{i}/{total}] Fetched {api_calls} matches, {lineups_found} with lineups")

    conn.commit()
    print(f"  Lineups sync complete. API calls: {api_calls}, matches with lineups: {lineups_found}")


def sync_all(conn: sqlite3.Connection, api_key: str, rate_limiter: RateLimiter,
             competitions: list[str], seasons: list[int]):
    sync_teams(conn, api_key, rate_limiter, competitions, seasons)
    sync_matches(conn, api_key, rate_limiter, competitions, seasons)
    sync_lineups(conn, api_key, rate_limiter, competitions, seasons)


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------

def print_stats(conn: sqlite3.Connection):
    print("\n=== football-data.org Cache Statistics ===\n")

    tables = [
        ("api_responses", "API Responses (cached)"),
        ("competitions", "Competitions"),
        ("teams", "Teams"),
        ("team_competitions", "Team-Competition-Season links"),
        ("persons", "Persons"),
        ("matches", "Matches"),
        ("match_lineups", "Match Lineup entries"),
        ("sync_status", "Sync status entries"),
    ]

    for table, label in tables:
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {label:40s} {count:>8,}")

    # HTTP status breakdown
    print("\n  API response status breakdown:")
    rows = conn.execute(
        "SELECT http_status, COUNT(*) FROM api_responses GROUP BY http_status ORDER BY http_status"
    ).fetchall()
    for status, count in rows:
        print(f"    HTTP {status}: {count:,}")

    # Competitions with data
    print("\n  Competitions with team data:")
    rows = conn.execute("""
        SELECT c.code, c.name, COUNT(DISTINCT tc.season) as seasons, COUNT(DISTINCT tc.team_id) as teams
        FROM competitions c
        JOIN team_competitions tc ON c.id = tc.competition_id
        GROUP BY c.id ORDER BY c.code
    """).fetchall()
    for code, name, season_count, team_count in rows:
        print(f"    {code:5s} {name:30s} {season_count:3d} seasons, {team_count:4d} teams")

    # Match stats
    print("\n  Matches by status:")
    rows = conn.execute(
        "SELECT status, COUNT(*) FROM matches GROUP BY status ORDER BY COUNT(*) DESC"
    ).fetchall()
    for status, count in rows:
        print(f"    {status or 'NULL':20s} {count:>8,}")

    # Lineup coverage
    matches_with_lineups = conn.execute(
        "SELECT COUNT(DISTINCT match_id) FROM match_lineups"
    ).fetchone()[0]
    total_finished = conn.execute(
        "SELECT COUNT(*) FROM matches WHERE status = 'FINISHED'"
    ).fetchone()[0]
    print(f"\n  Lineup coverage: {matches_with_lineups:,} / {total_finished:,} finished matches")

    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract data from football-data.org free API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"Free tier competitions: {', '.join(FREE_TIER_COMPETITIONS)}",
    )
    parser.add_argument("--api-key", help="API key (overrides env var / .env)")
    parser.add_argument("--db", default=DEFAULT_DB_PATH, help=f"Database path (default: {DEFAULT_DB_PATH})")

    sub = parser.add_subparsers(dest="command", required=True)

    # Common arguments for sync commands
    def add_sync_args(p):
        p.add_argument("--competitions", nargs="+", default=FREE_TIER_COMPETITIONS,
                        metavar="CODE", help="Competition codes to sync")
        p.add_argument("--seasons", nargs="+", type=int, default=DEFAULT_SEASONS,
                        metavar="YEAR", help="Seasons to sync (e.g. 2020 2021)")

    p_teams = sub.add_parser("sync-teams", help="Fetch teams per competition/season")
    add_sync_args(p_teams)

    p_matches = sub.add_parser("sync-matches", help="Fetch matches per competition/season")
    add_sync_args(p_matches)

    p_lineups = sub.add_parser("sync-lineups", help="Fetch lineup data for individual matches")
    add_sync_args(p_lineups)

    p_all = sub.add_parser("sync-all", help="Run teams, matches, and lineups sync in order")
    add_sync_args(p_all)

    sub.add_parser("stats", help="Print summary statistics")
    sub.add_parser("reparse", help="Re-parse all cached responses to extract data (e.g. after schema changes)")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    conn = init_db(args.db)

    if args.command == "stats":
        print_stats(conn)
        conn.close()
        return

    if args.command == "reparse":
        print("\n=== Re-parsing cached responses ===")
        responses, persons = reparse_teams(conn)
        print(f"  Re-parsed {responses} team responses, found {persons} player entries")
        print_stats(conn)
        conn.close()
        return

    api_key = resolve_api_key(args.api_key)
    rate_limiter = RateLimiter(max_requests=10, window_seconds=60)

    competitions = args.competitions
    seasons = args.seasons

    # Validate competition codes
    invalid = [c for c in competitions if c not in FREE_TIER_COMPETITIONS]
    if invalid:
        print(f"Warning: {', '.join(invalid)} not in free tier. Requests may fail.")

    print(f"Database: {args.db}")
    print(f"Competitions: {', '.join(competitions)}")
    print(f"Seasons: {min(seasons)}-{max(seasons)} ({len(seasons)} seasons)")

    dispatch = {
        "sync-teams": sync_teams,
        "sync-matches": sync_matches,
        "sync-lineups": sync_lineups,
        "sync-all": sync_all,
    }

    dispatch[args.command](conn, api_key, rate_limiter, competitions, seasons)
    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
