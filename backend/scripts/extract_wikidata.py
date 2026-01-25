"""
Script to extract football player data from Wikidata and populate the SQLite database.

This script queries Wikidata for:
- Players from top 5 European men's leagues (since 2000)
- Women's football players from major leagues

Run this script periodically to refresh the database.
"""

import requests
import sqlite3
import unicodedata
import re
import time
from pathlib import Path
from typing import Optional
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.models.database import get_db_connection, init_database, DATABASE_PATH

WIKIDATA_ENDPOINT = "https://query.wikidata.org/sparql"

HEADERS = {
    "Accept": "application/sparql-results+json",
    "User-Agent": "SoccerPlayerApp/1.0 (personal project for naming 1000 soccer players)"
}

# Men's league Wikidata IDs
MENS_LEAGUES = {
    "Premier League": "Q9448",
    "La Liga": "Q324867",
    "Bundesliga": "Q82595",
    "Serie A": "Q15804",
    "Ligue 1": "Q13394",
}


def normalize_name(name: str) -> str:
    """
    Normalize a name for matching:
    - Convert to lowercase
    - Remove accents/diacritics
    - Remove extra whitespace
    """
    # Normalize unicode and remove accents
    normalized = unicodedata.normalize('NFKD', name)
    normalized = ''.join(c for c in normalized if not unicodedata.combining(c))
    # Lowercase and clean whitespace
    normalized = normalized.lower().strip()
    normalized = re.sub(r'\s+', ' ', normalized)
    return normalized


def extract_first_last_name(full_name: str) -> tuple[Optional[str], Optional[str]]:
    """
    Attempt to extract first and last name from a full name.
    This is a simple heuristic - assumes "First Last" format.
    """
    parts = full_name.strip().split()
    if len(parts) >= 2:
        return parts[0], ' '.join(parts[1:])
    elif len(parts) == 1:
        return None, parts[0]  # Single name like "Ronaldo"
    return None, None


def run_sparql_query(query: str, max_retries: int = 3) -> list[dict]:
    """
    Run a SPARQL query against Wikidata with retry logic.
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(
                WIKIDATA_ENDPOINT,
                params={"query": query},
                headers=HEADERS,
                timeout=120
            )

            if response.status_code == 200:
                data = response.json()
                return data["results"]["bindings"]
            elif response.status_code == 429:  # Rate limited
                wait_time = 60 * (attempt + 1)
                print(f"Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"Error {response.status_code}: {response.text[:200]}")
                time.sleep(10)

        except requests.exceptions.Timeout:
            print(f"Timeout on attempt {attempt + 1}")
            time.sleep(30)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)

    return []


def fetch_mens_league_players(league_name: str, league_id: str, min_year: int = 2000) -> list[dict]:
    """
    Fetch players from a men's league who played since min_year.
    """
    print(f"\nFetching players from {league_name}...")

    # Query players with their basic info
    query = f"""
    SELECT DISTINCT ?player ?playerLabel ?nationalityLabel ?positionLabel ?birthDate ?wikidataId
    WHERE {{
      # Get the Wikidata ID
      BIND(REPLACE(STR(?player), "http://www.wikidata.org/entity/", "") AS ?wikidataId)

      ?player wdt:P106 wd:Q937857 .  # occupation: association football player

      # Played for a club in this league
      ?player p:P54 ?clubStatement .
      ?clubStatement ps:P54 ?club .
      ?club wdt:P118 wd:{league_id} .

      # Optional: filter by time period (if start time is available)
      OPTIONAL {{ ?clubStatement pq:P580 ?startTime . }}

      OPTIONAL {{ ?player wdt:P27 ?nationality . }}
      OPTIONAL {{ ?player wdt:P413 ?position . }}
      OPTIONAL {{ ?player wdt:P569 ?birthDate . }}

      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
    }}
    """

    results = run_sparql_query(query)
    print(f"  Found {len(results)} raw results")

    # Deduplicate by player (same player may appear multiple times for different clubs)
    players = {}
    for result in results:
        wikidata_id = result.get("wikidataId", {}).get("value")
        if not wikidata_id:
            continue

        if wikidata_id not in players:
            name = result.get("playerLabel", {}).get("value", "")
            if not name or name.startswith("Q"):  # Skip if no label
                continue

            players[wikidata_id] = {
                "wikidata_id": wikidata_id,
                "name": name,
                "nationality": result.get("nationalityLabel", {}).get("value"),
                "position": result.get("positionLabel", {}).get("value"),
                "birth_date": result.get("birthDate", {}).get("value", "")[:10] if result.get("birthDate") else None,
                "gender": "male",
                "league": league_name,
            }

    print(f"  Deduplicated to {len(players)} unique players")
    return list(players.values())


def fetch_womens_players(limit: int = 10000) -> list[dict]:
    """
    Fetch women's football players.
    """
    print(f"\nFetching women's football players...")

    query = f"""
    SELECT DISTINCT ?player ?playerLabel ?nationalityLabel ?positionLabel ?birthDate ?wikidataId
    WHERE {{
      BIND(REPLACE(STR(?player), "http://www.wikidata.org/entity/", "") AS ?wikidataId)

      ?player wdt:P106 wd:Q937857 .  # occupation: association football player
      ?player wdt:P21 wd:Q6581072 .  # female

      # Must have played for at least one club
      ?player wdt:P54 ?club .

      OPTIONAL {{ ?player wdt:P27 ?nationality . }}
      OPTIONAL {{ ?player wdt:P413 ?position . }}
      OPTIONAL {{ ?player wdt:P569 ?birthDate . }}

      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
    }}
    LIMIT {limit}
    """

    results = run_sparql_query(query)
    print(f"  Found {len(results)} raw results")

    players = {}
    for result in results:
        wikidata_id = result.get("wikidataId", {}).get("value")
        if not wikidata_id:
            continue

        if wikidata_id not in players:
            name = result.get("playerLabel", {}).get("value", "")
            if not name or name.startswith("Q"):
                continue

            players[wikidata_id] = {
                "wikidata_id": wikidata_id,
                "name": name,
                "nationality": result.get("nationalityLabel", {}).get("value"),
                "position": result.get("positionLabel", {}).get("value"),
                "birth_date": result.get("birthDate", {}).get("value", "")[:10] if result.get("birthDate") else None,
                "gender": "female",
                "league": "Women's Football",
            }

    print(f"  Deduplicated to {len(players)} unique players")
    return list(players.values())


def fetch_player_club_history(wikidata_id: str) -> list[dict]:
    """
    Fetch a player's complete club history.
    """
    query = f"""
    SELECT ?clubLabel ?clubId ?startTime ?endTime ?isNationalTeam
    WHERE {{
      wd:{wikidata_id} p:P54 ?clubStatement .
      ?clubStatement ps:P54 ?club .

      BIND(REPLACE(STR(?club), "http://www.wikidata.org/entity/", "") AS ?clubId)

      OPTIONAL {{ ?clubStatement pq:P580 ?startTime . }}
      OPTIONAL {{ ?clubStatement pq:P582 ?endTime . }}

      # Check if it's a national team
      OPTIONAL {{
        ?club wdt:P31 wd:Q6979593 .  # instance of national association football team
        BIND(true AS ?isNationalTeam)
      }}

      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
    }}
    ORDER BY ?startTime
    """

    results = run_sparql_query(query)

    clubs = []
    for result in results:
        club_name = result.get("clubLabel", {}).get("value", "")
        if not club_name or club_name.startswith("Q"):
            continue

        clubs.append({
            "wikidata_id": result.get("clubId", {}).get("value"),
            "name": club_name,
            "start_date": result.get("startTime", {}).get("value", "")[:10] if result.get("startTime") else None,
            "end_date": result.get("endTime", {}).get("value", "")[:10] if result.get("endTime") else None,
            "is_national_team": result.get("isNationalTeam", {}).get("value") == "true",
        })

    return clubs


def insert_player(conn: sqlite3.Connection, player: dict) -> Optional[int]:
    """
    Insert a player into the database. Returns the player ID.
    """
    cursor = conn.cursor()

    first_name, last_name = extract_first_last_name(player["name"])
    normalized = normalize_name(player["name"])

    try:
        cursor.execute("""
            INSERT OR IGNORE INTO players
            (wikidata_id, name, normalized_name, first_name, last_name,
             nationality, position, birth_date, gender)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            player["wikidata_id"],
            player["name"],
            normalized,
            first_name,
            last_name,
            player.get("nationality"),
            player.get("position"),
            player.get("birth_date"),
            player.get("gender", "male"),
        ))

        if cursor.rowcount > 0:
            return cursor.lastrowid

        # If insert was ignored (duplicate), get the existing ID
        cursor.execute("SELECT id FROM players WHERE wikidata_id = ?", (player["wikidata_id"],))
        row = cursor.fetchone()
        return row[0] if row else None

    except Exception as e:
        print(f"Error inserting player {player['name']}: {e}")
        return None


def insert_club(conn: sqlite3.Connection, club: dict) -> Optional[int]:
    """
    Insert a club into the database. Returns the club ID.
    """
    cursor = conn.cursor()

    normalized = normalize_name(club["name"])

    try:
        cursor.execute("""
            INSERT OR IGNORE INTO clubs (wikidata_id, name, normalized_name)
            VALUES (?, ?, ?)
        """, (club["wikidata_id"], club["name"], normalized))

        if cursor.rowcount > 0:
            return cursor.lastrowid

        cursor.execute("SELECT id FROM clubs WHERE wikidata_id = ?", (club["wikidata_id"],))
        row = cursor.fetchone()
        return row[0] if row else None

    except Exception as e:
        print(f"Error inserting club {club['name']}: {e}")
        return None


def insert_player_club(conn: sqlite3.Connection, player_id: int, club_id: int, club_data: dict):
    """
    Insert a player-club relationship.
    """
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT OR IGNORE INTO player_clubs
            (player_id, club_id, start_date, end_date, is_national_team)
            VALUES (?, ?, ?, ?, ?)
        """, (
            player_id,
            club_id,
            club_data.get("start_date"),
            club_data.get("end_date"),
            club_data.get("is_national_team", False),
        ))
    except Exception as e:
        print(f"Error inserting player-club relationship: {e}")


def main(fetch_clubs: bool = True):
    """
    Main extraction process.

    Args:
        fetch_clubs: If True, also fetch club histories after player import.
    """
    print("=" * 60)
    print("Soccer Player Data Extraction from Wikidata")
    print("=" * 60)

    # Initialize database
    init_database()
    conn = get_db_connection()

    all_players = []

    # Fetch men's league players
    for league_name, league_id in MENS_LEAGUES.items():
        players = fetch_mens_league_players(league_name, league_id)
        all_players.extend(players)
        time.sleep(2)  # Be nice to Wikidata

    # Fetch women's players
    women_players = fetch_womens_players(limit=15000)
    all_players.extend(women_players)

    print(f"\n{'=' * 60}")
    print(f"Total players to process: {len(all_players)}")
    print("=" * 60)

    # Insert players
    processed = 0
    for player in all_players:
        insert_player(conn, player)

        processed += 1
        if processed % 1000 == 0:
            conn.commit()
            print(f"  Processed {processed}/{len(all_players)} players...")

    conn.commit()
    conn.close()

    print(f"\n{'=' * 60}")
    print(f"Player extraction complete!")
    print(f"Database saved to: {DATABASE_PATH}")
    print("=" * 60)

    # Optionally fetch club histories
    if fetch_clubs:
        print("\nNow fetching club histories...")
        print("(This may take a while - run fetch_club_histories.py separately if needed)\n")
        from fetch_club_histories import main as fetch_club_histories_main
        fetch_club_histories_main()


def fetch_club_histories_batch(player_ids: list[str], batch_size: int = 50):
    """
    Fetch club histories for multiple players in batches.
    This is more efficient than individual queries.
    """
    # This would be implemented for production use
    # For now, we'll focus on getting the basic player data in
    pass


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Extract soccer player data from Wikidata")
    parser.add_argument("--no-clubs", action="store_true",
                        help="Skip fetching club histories (faster, can run fetch_club_histories.py later)")
    args = parser.parse_args()
    main(fetch_clubs=not args.no_clubs)
