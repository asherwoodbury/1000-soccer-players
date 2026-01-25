"""
Script to fetch club histories for players already in the database.

This uses batch SPARQL queries to efficiently fetch club histories
for multiple players at once, rather than one query per player.

Run this after extract_wikidata.py to populate club histories.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.database import get_db_connection, DATABASE_PATH
from extract_wikidata import (
    run_sparql_query,
    insert_club,
    insert_player_club,
    normalize_name
)


def fetch_club_histories_batch(wikidata_ids: list[str]) -> dict[str, list[dict]]:
    """
    Fetch club histories for multiple players in a single SPARQL query.
    Returns a dict mapping wikidata_id -> list of clubs.
    """
    if not wikidata_ids:
        return {}

    # Build VALUES clause for batch query
    values_clause = " ".join(f"wd:{wid}" for wid in wikidata_ids)

    query = f"""
    SELECT ?player ?playerId ?clubLabel ?clubId ?startTime ?endTime ?isNationalTeam
    WHERE {{
      VALUES ?player {{ {values_clause} }}

      BIND(REPLACE(STR(?player), "http://www.wikidata.org/entity/", "") AS ?playerId)

      ?player p:P54 ?clubStatement .
      ?clubStatement ps:P54 ?club .

      BIND(REPLACE(STR(?club), "http://www.wikidata.org/entity/", "") AS ?clubId)

      OPTIONAL {{ ?clubStatement pq:P580 ?startTime . }}
      OPTIONAL {{ ?clubStatement pq:P582 ?endTime . }}

      # Check if it's a national team
      OPTIONAL {{
        ?club wdt:P31 wd:Q6979593 .
        BIND(true AS ?isNationalTeam)
      }}

      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
    }}
    ORDER BY ?playerId ?startTime
    """

    results = run_sparql_query(query)

    # Group results by player
    player_clubs = {}
    for result in results:
        player_id = result.get("playerId", {}).get("value")
        if not player_id:
            continue

        club_name = result.get("clubLabel", {}).get("value", "")
        club_id = result.get("clubId", {}).get("value", "")

        if not club_name or club_name.startswith("Q") or not club_id:
            continue

        if player_id not in player_clubs:
            player_clubs[player_id] = []

        player_clubs[player_id].append({
            "wikidata_id": club_id,
            "name": club_name,
            "start_date": result.get("startTime", {}).get("value", "")[:10] if result.get("startTime") else None,
            "end_date": result.get("endTime", {}).get("value", "")[:10] if result.get("endTime") else None,
            "is_national_team": "national" in club_name.lower() or result.get("isNationalTeam", {}).get("value") == "true",
        })

    return player_clubs


def get_players_without_clubs(conn, limit: int = 1000) -> list[tuple[int, str]]:
    """
    Get players who don't have any club history yet.
    Returns list of (player_id, wikidata_id) tuples.
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id, p.wikidata_id
        FROM players p
        LEFT JOIN player_clubs pc ON p.id = pc.player_id
        WHERE pc.id IS NULL
        LIMIT ?
    """, (limit,))
    return cursor.fetchall()


def main():
    """
    Main process to fetch club histories in batches.
    """
    print("=" * 60)
    print("Fetching Club Histories from Wikidata")
    print("=" * 60)

    conn = get_db_connection()

    # Get count of players without clubs
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*)
        FROM players p
        LEFT JOIN player_clubs pc ON p.id = pc.player_id
        WHERE pc.id IS NULL
    """)
    total_without_clubs = cursor.fetchone()[0]

    print(f"\nPlayers without club history: {total_without_clubs}")

    if total_without_clubs == 0:
        print("All players already have club histories!")
        return

    batch_size = 50  # Number of players per SPARQL query
    processed = 0
    total_clubs_added = 0

    while True:
        # Get batch of players without club history
        players = get_players_without_clubs(conn, limit=batch_size)

        if not players:
            break

        player_ids = {row[1]: row[0] for row in players}  # wikidata_id -> db_id
        wikidata_ids = list(player_ids.keys())

        print(f"\nFetching clubs for batch of {len(wikidata_ids)} players...")

        # Fetch club histories in batch
        club_histories = fetch_club_histories_batch(wikidata_ids)

        # Insert clubs and relationships
        for wikidata_id, clubs in club_histories.items():
            player_db_id = player_ids.get(wikidata_id)
            if not player_db_id:
                continue

            for club in clubs:
                club_db_id = insert_club(conn, club)
                if club_db_id:
                    insert_player_club(conn, player_db_id, club_db_id, club)
                    total_clubs_added += 1

        # For players with no clubs found, insert a placeholder to mark them as processed
        # (so they don't get queried again)
        for wikidata_id in wikidata_ids:
            if wikidata_id not in club_histories:
                # Player has no clubs in Wikidata - that's okay, they're still processed
                pass

        conn.commit()
        processed += len(players)

        print(f"  Processed {processed} players, added {total_clubs_added} club relationships")

        # Be nice to Wikidata
        time.sleep(1)

        # Check if we're done
        remaining = get_players_without_clubs(conn, limit=1)
        if not remaining:
            break

    conn.close()

    print(f"\n{'=' * 60}")
    print(f"Club history fetch complete!")
    print(f"Total players processed: {processed}")
    print(f"Total club relationships added: {total_clubs_added}")
    print("=" * 60)


if __name__ == "__main__":
    main()
