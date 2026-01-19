"""
Quick test extraction with limited data to verify the pipeline works.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.database import get_db_connection, init_database, DATABASE_PATH
from extract_wikidata import (
    run_sparql_query,
    normalize_name,
    extract_first_last_name,
    insert_player,
    insert_club,
    insert_player_club
)


def fetch_sample_players():
    """Fetch a small sample of Premier League players with club history."""

    print("Fetching sample Premier League players...")

    query = """
    SELECT DISTINCT ?player ?playerLabel ?nationalityLabel ?positionLabel ?birthDate ?wikidataId
    WHERE {
      BIND(REPLACE(STR(?player), "http://www.wikidata.org/entity/", "") AS ?wikidataId)

      ?player wdt:P106 wd:Q937857 .
      ?player p:P54 ?clubStatement .
      ?clubStatement ps:P54 ?club .
      ?club wdt:P118 wd:Q9448 .  # Premier League

      OPTIONAL { ?player wdt:P27 ?nationality . }
      OPTIONAL { ?player wdt:P413 ?position . }
      OPTIONAL { ?player wdt:P569 ?birthDate . }

      SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
    }
    LIMIT 100
    """

    results = run_sparql_query(query)
    print(f"Got {len(results)} results")

    players = {}
    for result in results:
        wikidata_id = result.get("wikidataId", {}).get("value")
        if not wikidata_id or wikidata_id in players:
            continue

        name = result.get("playerLabel", {}).get("value", "")
        if not name or name.startswith("Q"):
            continue

        players[wikidata_id] = {
            "wikidata_id": wikidata_id,
            "name": name,
            "nationality": result.get("nationalityLabel", {}).get("value"),
            "position": result.get("positionLabel", {}).get("value"),
            "birth_date": result.get("birthDate", {}).get("value", "")[:10] if result.get("birthDate") else None,
            "gender": "male",
        }

    return list(players.values())


def fetch_player_clubs(wikidata_id: str):
    """Fetch clubs for a single player."""

    query = f"""
    SELECT ?clubLabel ?clubId ?startTime ?endTime
    WHERE {{
      wd:{wikidata_id} p:P54 ?clubStatement .
      ?clubStatement ps:P54 ?club .
      BIND(REPLACE(STR(?club), "http://www.wikidata.org/entity/", "") AS ?clubId)
      OPTIONAL {{ ?clubStatement pq:P580 ?startTime . }}
      OPTIONAL {{ ?clubStatement pq:P582 ?endTime . }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
    }}
    ORDER BY ?startTime
    """

    results = run_sparql_query(query)

    clubs = []
    for result in results:
        club_name = result.get("clubLabel", {}).get("value", "")
        club_id = result.get("clubId", {}).get("value", "")
        if not club_name or club_name.startswith("Q") or not club_id:
            continue

        clubs.append({
            "wikidata_id": club_id,
            "name": club_name,
            "start_date": result.get("startTime", {}).get("value", "")[:10] if result.get("startTime") else None,
            "end_date": result.get("endTime", {}).get("value", "")[:10] if result.get("endTime") else None,
            "is_national_team": "national" in club_name.lower(),
        })

    return clubs


def main():
    print("=" * 50)
    print("Sample Data Extraction Test")
    print("=" * 50)

    # Initialize database
    init_database()
    conn = get_db_connection()

    # Fetch sample players
    players = fetch_sample_players()
    print(f"\nProcessing {len(players)} unique players...")

    # Insert players and their club histories
    for i, player in enumerate(players[:20]):  # Just do 20 for the test
        player_id = insert_player(conn, player)

        if player_id:
            # Fetch and insert club history
            clubs = fetch_player_clubs(player["wikidata_id"])
            for club in clubs:
                club_id = insert_club(conn, club)
                if club_id:
                    insert_player_club(conn, player_id, club_id, club)

            print(f"  {i+1}. {player['name']} - {len(clubs)} clubs")

        conn.commit()

    conn.close()

    # Verify the data
    print("\n" + "=" * 50)
    print("Verification")
    print("=" * 50)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM players")
    print(f"Total players: {cursor.fetchone()[0]}")

    cursor.execute("SELECT COUNT(*) FROM clubs")
    print(f"Total clubs: {cursor.fetchone()[0]}")

    cursor.execute("SELECT COUNT(*) FROM player_clubs")
    print(f"Total player-club relationships: {cursor.fetchone()[0]}")

    print("\nSample player with clubs:")
    cursor.execute("""
        SELECT p.name, p.nationality, p.position,
               GROUP_CONCAT(c.name, ', ') as clubs
        FROM players p
        LEFT JOIN player_clubs pc ON p.id = pc.player_id
        LEFT JOIN clubs c ON pc.club_id = c.id
        GROUP BY p.id
        LIMIT 3
    """)

    for row in cursor.fetchall():
        print(f"  {row['name']} ({row['nationality']}) - {row['position']}")
        print(f"    Clubs: {row['clubs']}")

    conn.close()
    print(f"\nDatabase saved to: {DATABASE_PATH}")


if __name__ == "__main__":
    main()
