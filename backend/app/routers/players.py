"""
Player lookup and search endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
import unicodedata
import re
from datetime import datetime

from app.models.database import get_db_connection


def calculate_club_duration_years(start_date: Optional[str], end_date: Optional[str]) -> float:
    """
    Calculate the duration in years a player was at a club.
    If end_date is None, assumes the player is still at the club (uses current date).
    If start_date is None, returns 0.
    """
    if not start_date:
        return 0.0

    try:
        start = datetime.strptime(start_date[:10], "%Y-%m-%d")
    except (ValueError, TypeError):
        # Try year-only format
        try:
            start = datetime.strptime(start_date[:4], "%Y")
        except (ValueError, TypeError):
            return 0.0

    if end_date:
        try:
            end = datetime.strptime(end_date[:10], "%Y-%m-%d")
        except (ValueError, TypeError):
            try:
                end = datetime.strptime(end_date[:4], "%Y")
            except (ValueError, TypeError):
                end = datetime.now()
    else:
        end = datetime.now()

    duration_days = (end - start).days
    return max(0.0, duration_days / 365.25)


def calculate_career_span(clubs: list) -> Optional[str]:
    """
    Calculate career span from club history.
    Returns a string like "2005-2020" or "2018-present".
    """
    if not clubs:
        return None

    start_years = []
    end_years = []

    for club in clubs:
        if club.start_date:
            try:
                start_years.append(int(club.start_date[:4]))
            except (ValueError, TypeError):
                pass
        if club.end_date:
            try:
                end_years.append(int(club.end_date[:4]))
            except (ValueError, TypeError):
                pass

    if not start_years:
        return None

    earliest = min(start_years)

    # Check if any club has no end date (still active)
    has_active_club = any(c.end_date is None for c in clubs)

    if has_active_club:
        return f"{earliest}-present"
    elif end_years:
        latest = max(end_years)
        return f"{earliest}-{latest}"
    else:
        return f"{earliest}-present"

router = APIRouter()


def normalize_name(name: str) -> str:
    """Normalize a name for matching."""
    normalized = unicodedata.normalize('NFKD', name)
    normalized = ''.join(c for c in normalized if not unicodedata.combining(c))
    normalized = normalized.lower().strip()
    normalized = re.sub(r'\s+', ' ', normalized)
    return normalized


class ClubHistory(BaseModel):
    name: str
    start_date: Optional[str]
    end_date: Optional[str]
    is_national_team: bool


class PlayerResponse(BaseModel):
    id: int
    name: str
    nationality: Optional[str]
    position: Optional[str]
    clubs: list[ClubHistory]
    top_clubs: list[str]  # Top 3 clubs by duration (years)
    career_span: Optional[str]  # e.g., "2005-2020" or "2018-present"


class PlayerLookupResult(BaseModel):
    found: bool
    player: Optional[PlayerResponse]
    message: str


class AmbiguousPlayerResult(BaseModel):
    found: bool
    ambiguous: bool
    count: int
    message: str


@router.get("/lookup", response_model=PlayerLookupResult | AmbiguousPlayerResult)
async def lookup_player(name: str = Query(..., min_length=2, description="Player name to look up")):
    """
    Look up a player by name.

    - If exact match found: returns player data
    - If multiple matches: returns "be more specific" message
    - If no match: returns not found
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    normalized = normalize_name(name)

    # Try exact normalized match first
    cursor.execute("""
        SELECT id, name, nationality, position, wikidata_id
        FROM players
        WHERE normalized_name = ?
    """, (normalized,))

    rows = cursor.fetchall()

    if len(rows) == 0:
        # Try partial match (starts with)
        cursor.execute("""
            SELECT id, name, nationality, position, wikidata_id
            FROM players
            WHERE normalized_name LIKE ?
            LIMIT 10
        """, (normalized + "%",))
        rows = cursor.fetchall()

    if len(rows) == 0:
        conn.close()
        return PlayerLookupResult(
            found=False,
            player=None,
            message="Player not found. Check the spelling and try again."
        )

    if len(rows) > 1:
        # Check if they're actually different players (different nationalities)
        unique_players = {(row['name'], row['nationality']) for row in rows}

        if len(unique_players) > 1:
            conn.close()
            return AmbiguousPlayerResult(
                found=False,
                ambiguous=True,
                count=len(unique_players),
                message=f"Found {len(unique_players)} players with similar names. Please be more specific (try including nationality or full name)."
            )

    # Found exactly one player (or multiple entries for same player)
    player = rows[0]
    player_id = player['id']

    # Get club history
    cursor.execute("""
        SELECT c.name, pc.start_date, pc.end_date, pc.is_national_team
        FROM player_clubs pc
        JOIN clubs c ON pc.club_id = c.id
        WHERE pc.player_id = ?
        ORDER BY pc.start_date
    """, (player_id,))

    club_rows = cursor.fetchall()
    conn.close()

    clubs = [
        ClubHistory(
            name=row['name'],
            start_date=row['start_date'],
            end_date=row['end_date'],
            is_national_team=bool(row['is_national_team'])
        )
        for row in club_rows
    ]

    # Calculate top clubs by duration (non-national teams only)
    non_national_clubs = [c for c in clubs if not c.is_national_team]

    # Calculate duration for each club and sort by duration
    club_durations = []
    for club in non_national_clubs:
        duration = calculate_club_duration_years(club.start_date, club.end_date)
        club_durations.append((club.name, duration))

    # Sort by duration descending, take top 3 unique club names
    club_durations.sort(key=lambda x: x[1], reverse=True)
    seen_clubs = set()
    top_clubs = []
    for club_name, _ in club_durations:
        if club_name not in seen_clubs:
            seen_clubs.add(club_name)
            top_clubs.append(club_name)
            if len(top_clubs) >= 3:
                break

    # Calculate career span
    career_span = calculate_career_span(clubs)

    return PlayerLookupResult(
        found=True,
        player=PlayerResponse(
            id=player_id,
            name=player['name'],
            nationality=player['nationality'],
            position=player['position'],
            clubs=clubs,
            top_clubs=top_clubs,
            career_span=career_span
        ),
        message="Player found!"
    )


@router.get("/stats")
async def get_player_stats():
    """Get overall statistics about the player database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as count FROM players")
    total_players = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM clubs")
    total_clubs = cursor.fetchone()['count']

    cursor.execute("""
        SELECT nationality, COUNT(*) as count
        FROM players
        WHERE nationality IS NOT NULL
        GROUP BY nationality
        ORDER BY count DESC
        LIMIT 10
    """)
    top_nationalities = [{"nationality": row['nationality'], "count": row['count']} for row in cursor.fetchall()]

    cursor.execute("""
        SELECT position, COUNT(*) as count
        FROM players
        WHERE position IS NOT NULL
        GROUP BY position
        ORDER BY count DESC
        LIMIT 10
    """)
    top_positions = [{"position": row['position'], "count": row['count']} for row in cursor.fetchall()]

    conn.close()

    return {
        "total_players": total_players,
        "total_clubs": total_clubs,
        "top_nationalities": top_nationalities,
        "top_positions": top_positions
    }
